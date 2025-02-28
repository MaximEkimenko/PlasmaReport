"""Routers сервиса master."""

from typing import Annotated

from fastapi import Query, Depends, APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import EmptyAnswerError, AlchemyDatabaseError, ServerNotImplementedError, UserAlreadyExistsException
from master.dao import FioDoerDAO
from techman.dao import PartDAO, ProgramDAO
from master.enums import Jobs
from logger_config import log
from techman.enums import ProgramStatus
from master.schemas import SFioDoer, SProgramsStatus
from dependencies.dao_dep import get_session_with_commit, get_session_without_commit

router = APIRouter()


@router.get("/get_programs_for_assignment", tags=["master"])
async def get_programs_for_assignment(select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                                      # user_data: Annotated[User, Depends(get_current_techman_user)]
                                      ) -> list[dict]:
    """Получение списка программ со статусом CREATED (создана).

    Для последующей передачи в работу и назначения исполнителя мастером.
    """
    programs_select_table = ProgramDAO(session=select_session)
    result = await programs_select_table.find_all(filters=SProgramsStatus(program_status=ProgramStatus.CREATED))
    programs_to_assign = [program.to_dict() for program in result]
    if not programs_to_assign:
        raise EmptyAnswerError(detail="Нет программ для передачи в работу.")

    return programs_to_assign


@router.get("/get_parts_by_program_id", tags=["master", "logist"])
async def get_parts_by_program_id(program_id: int,
                                  select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                                  # user_data: Annotated[User, Depends(get_current_techman_user)]
                                  ) -> list[dict]:
    """Получение списка деталей программы по ее id.

    Пример ввода: 1
    """
    parts_select_table = PartDAO(session=select_session)
    parts = await parts_select_table.get_joined_part_data_by_programs_ids_list([program_id])
    if not parts:
        raise EmptyAnswerError(detail="Нет деталей для данной программы.")
    return parts


@router.get("/get_parts_by_statuses", tags=["master", "logist"])
async def get_parts_by_statuses(select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                                include_program_statuses: Annotated[tuple[str, ...],
                                Query()] = (ProgramStatus.CREATED,
                                            ProgramStatus.UNASSIGNED,
                                            ProgramStatus.ASSIGNED,
                                            ProgramStatus.ACTIVE,
                                            ),
                                # user_data: Annotated[User, Depends(get_current_techman_user)]
                                ) -> list[dict]:
    """Получение программ по списку статусов.

    include_program_statuses = список статусов программы, которые должны быть включены в выборку.
    По молчанию =("создана",
                "не распределена",
               "распределена",
               "в работе").
    """
    parts_select_table = PartDAO(session=select_session)
    parts = await parts_select_table.get_joined_part_data_statuses(include_statuses=include_program_statuses)
    if not parts:
        raise EmptyAnswerError(detail="Нет деталей в данной выборке.")
    return parts


@router.post("/create_doer", tags=["master"])
async def create_doer(fio_doer: SFioDoer,
                      add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
                      select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                      # user_data: Annotated[User, Depends(get_current_techman_user)]
                      ) -> dict:
    """Создание исполнителя для выполнения программы.

    Пример ввода:
    `{"fio_doer": "Иванов И.И.", "position": "оператор"}`.
    Поле position необязательное и по умолчанию заполняется 'оператор'.
    """
    fio_select_table = FioDoerDAO(session=select_session)
    existing_user = await fio_select_table.find_one_or_none(fio_doer)
    if existing_user:
        raise UserAlreadyExistsException

    fio_create_table = FioDoerDAO(session=add_session)
    await fio_create_table.add(fio_doer)

    return {"msg": f"Пользователь {fio_doer.fio_doer} успешно создан."}


@router.get("/get_doers", tags=["master"])
async def get_doers_list(select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                         # user_data: Annotated[User, Depends(get_current_techman_user)]
                         ) -> list[dict]:
    """Получение списка всех исполнителей."""
    fio_select_table = FioDoerDAO(session=select_session)
    doers = await fio_select_table.find_all(filters=SFioDoer(position=Jobs.OPERATOR))
    if not doers:
        raise EmptyAnswerError(detail="Список операторов пуст.")
    return [fio_doer.to_dict() for fio_doer in doers]


@router.get("/get_programs_for_assignment_and_doers", tags=["master"])
async def get_programs_for_assignment_and_doers(
        select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
        # user_data: Annotated[User, Depends(get_current_techman_user)]
) -> dict:
    """Получение словаря со списками программ и исполнителей.

    Пример ответа:
     {
        programs: [список всех программ со статусом CREATED]
        doers: [список всех операторов (doer c с JOB = 'operator')]
    }
    """
    programs_select_table = ProgramDAO(session=select_session)
    result = await programs_select_table.find_all(filters=SProgramsStatus(program_status=ProgramStatus.CREATED))
    programs_to_assign = [program.to_dict() for program in result]
    if not programs_to_assign:
        raise EmptyAnswerError(detail="Нет программ для передачи в работу.")

    fio_select_table = FioDoerDAO(session=select_session)
    doers = await fio_select_table.find_all(filters=SFioDoer(position=Jobs.OPERATOR))
    if not doers:
        raise EmptyAnswerError(detail="Список операторов пуст.")
    doers = [fio_doer.to_dict() for fio_doer in doers]

    return {"programs": programs_to_assign, "doers": doers}


@router.post("/assign_program", tags=["master"])
async def assign_program(program_ids_with_fios_id: list[dict],
                         # program_ids_with_fios_id: list[SProgramIDWithFios],
                         add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
                         select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                         # user_data: Annotated[User, Depends(get_current_techman_user)]
                         ) -> dict:
    """Передача программ в работу оператору мастером (распределение).

    Перевод программы в статус ASSIGNED.

    Пример ввода:
    `[
        {"id":13, "fio_doers_ids": [1, 2, 3]},
        {"id":14, "fio_doers_ids": [4, 5, 6]}
    ]`
    """
    program_select_table = ProgramDAO(session=select_session)
    for program_id in [program_id_with_fio["id"] for program_id_with_fio in program_ids_with_fios_id]:
        exist_programs = await program_select_table.find_one_or_none_by_id(program_id)
        if not exist_programs:
            log.warning("Попытка обновления не существующей программы с id={program_id}.", program_id=program_id)
            raise EmptyAnswerError(detail=f"Программа с id {program_id} не найдена.")

    try:
        program_update_table = ProgramDAO(session=add_session)
        # await program_update_table.bulk_update(records=program_ids_with_fios_id)
        await program_update_table.update_doer_fios(program_ids_with_fios_id)
    except SQLAlchemyError as e:
        await add_session.rollback()
        log.error("Ошибка при работе с БД.")
        log.exception(e)
        raise AlchemyDatabaseError from e
    else:
        msg = "Программы успешно переданы в работу."
        log.success(msg)

    return {"msg": msg}


@router.post("/cancel_assign_program", tags=["master"])
async def cancel_assign_program(  # program_ids_with_fios_id: list[SProgramIDWithFio],
        # add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
        # select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
        # user_data: Annotated[User, Depends(get_current_techman_user)]
) -> None:
    """Отмена передачи программ в работу оператору мастером (отмена распределения).

    Перевод программы в статус CREATED. Отмена возможна только для программ со статусом ASSIGNED.

    # TODO после реализации основного процесса
    """
    return ServerNotImplementedError
