"""Routers сервиса master."""

from typing import Annotated

from fastapi import Query, Depends, APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.users import get_master_user
from exceptions import (
    EmptyAnswerError,
    WrongDoerIdsError,
    AlchemyDatabaseError,
    ServerNotImplementedError,
    UserAlreadyExistsException,
)
from master.dao import FioDoerDAO
from auth.models import User
from techman.dao import PartDAO, ProgramDAO
from master.enums import Jobs
from logger_config import log
from techman.enums import ProgramStatus
from master.schemas import SFioDoer, SProgramIDWithFios
from dependencies.dao_dep import get_session_with_commit, get_session_without_commit

router = APIRouter()


# @router.get("/get_programs_for_assignment", tags=["master"])
# async def get_programs_for_assignment(select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
#                                       # user_data: Annotated[User, Depends(get_current_techman_user)]
#                                       ) -> list[dict]:
#     """Получение списка программ со статусом CREATED (создана).
#
#     Для последующей передачи в работу и назначения исполнителя мастером.
#     """
#     programs_select_table = ProgramDAO(session=select_session)
#     result = await programs_select_table.get_all_with_doers(filter_dict={"program_status": ProgramStatus.ASSIGNED})
#     # programs_to_assign = [program.to_dict() | {"fio_doers": list(program.fio_doers)} for program in result]
#     # print(programs_to_assign)
#     if not result:
#         raise EmptyAnswerError(detail="Нет программ для передачи в работу.")
#
#     return result


@router.get("/get_parts_by_program_id", tags=["master", "logist"])
async def get_parts_by_program_id(program_id: int,
                                  select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                                  user_data: Annotated[User, Depends(get_master_user)],  # noqa ARG001
                                  fio_doer_id: int | None = None,
                                  ) -> list[dict]:
    """Получение списка деталей программы по ее id. С опциональным параметром fio_doer_id.

    Пример ввода: `1`.

    При передаче id исполнителя (fio_doer_id), который участвовал в программе, список fio_doers будет
    преобразован в словарь только с этим исполнителем. Если fio_doer_id не распределён в программе,
    то список останется бех изменений.
    """
    parts_select_table = PartDAO(session=select_session)
    parts = await parts_select_table.get_joined_part_data_by_programs_ids_list([program_id])
    if not parts:
        raise EmptyAnswerError(detail="Нет деталей для данной программы.")

    fio_doer_select_table = FioDoerDAO(session=select_session)
    one_fio_doer = await fio_doer_select_table.find_one_or_none_by_id(fio_doer_id)

    # фильтрация по исполнителю программы
    if fio_doer_id:
        for part in parts:
            doer_ids = [fio_doer["id"] for fio_doer in part["fio_doers"]]
            if one_fio_doer.id in doer_ids:
                part.update({"fio_doers": one_fio_doer.to_dict()})

    return parts


@router.get("/get_parts_by_statuses", tags=["master", "logist"])
async def get_parts_by_statuses(select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                                user_data: Annotated[User, Depends(get_master_user)],  # noqa ARG001
                                include_program_statuses: Annotated[tuple[str, ...],
                                Query()] = (ProgramStatus.CREATED,
                                            ProgramStatus.UNASSIGNED,
                                            ProgramStatus.ASSIGNED,
                                            ProgramStatus.ACTIVE,
                                            ),

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
                      user_data: Annotated[User, Depends(get_master_user)],  # noqa ARG001
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
                         user_data: Annotated[User, Depends(get_master_user)],  # noqa ARG001
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
        user_data: Annotated[User, Depends(get_master_user)],  # noqa ARG001
) -> dict:
    """Получение словаря со списками программ и исполнителей.

    Пример ответа:
     {
        programs: [список всех программ со статусом CREATED]
        doers: [список всех операторов (doer c с JOB = 'operator')]
    }
    """
    programs_select_table = ProgramDAO(session=select_session)
    allowed_statuses = [ProgramStatus.CREATED, ProgramStatus.UNASSIGNED, ProgramStatus.ASSIGNED, ProgramStatus.ACTIVE]
    programs_to_assign = await programs_select_table.get_all_with_doers(status_list=allowed_statuses)
    if not programs_to_assign:
        raise EmptyAnswerError(detail="Нет программ для передачи в работу.")

    fio_select_table = FioDoerDAO(session=select_session)
    doers = await fio_select_table.find_all(filters=SFioDoer(position=Jobs.OPERATOR))
    if not doers:
        raise EmptyAnswerError(detail="Список операторов пуст.")
    doers = [fio_doer.to_dict() for fio_doer in doers]

    return {"programs": programs_to_assign, "doers": doers}


@router.post("/assign_program", tags=["master"])
async def assign_program(
        program_ids_with_fios_id: list[SProgramIDWithFios],
        add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
        select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
        user_data: Annotated[User, Depends(get_master_user)],  # noqa ARG001
) -> dict:
    """Передача программ в работу оператору мастером (распределение).

    Перевод программы в статус ASSIGNED.

    Пример ввода:
    `[
        {
        "id":13,
         "fio_doers_ids": [1, 2, 3],
        "program_priority": "MEDIUM"
        },
        {
        "id":14,
        "fio_doers_ids": [4, 5, 6],
        "program_priority": "HIGH"
        }
    ]`
    program_priority - необязательный параметр и по умолчанию = LOW
    """
    # проверка на дубликаты id
    for line in program_ids_with_fios_id:
        fio_doers_ids = line.fio_doers_ids
        if len(set(fio_doers_ids)) != len(fio_doers_ids):
            raise WrongDoerIdsError

    program_select_table = ProgramDAO(session=select_session)
    for program_id in [program_id_with_fio.id for program_id_with_fio in program_ids_with_fios_id]:
        exist_programs = await program_select_table.find_one_or_none_by_id(program_id)
        if not exist_programs:
            log.warning("Попытка обновления не существующей программы с id={program_id}.", program_id=program_id)
            raise EmptyAnswerError(detail=f"Программа с id {program_id} не найдена.")

    try:
        program_update_table = ProgramDAO(session=add_session)
        await program_update_table.update_fio_doers(program_ids_with_fios_id)
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
        user_data: Annotated[User, Depends(get_master_user)],  # noqa ARG001
) -> None:
    """Отмена передачи программ в работу оператору мастером (отмена распределения).

    Перевод программы в статус CREATED. Отмена возможна только для программ со статусом ASSIGNED.

    # TODO после реализации основного процесса
    """
    return ServerNotImplementedError


@router.post("/update_assign_program", tags=["master"])
async def update_assign_program(  # program_ids_with_fios_id: list[SProgramIDWithFio],
        # add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
        # select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
        # user_data: Annotated[User, Depends(get_current_techman_user)]
        user_data: Annotated[User, Depends(get_master_user)],  # noqa ARG001
) -> None:
    """Обновление передачи программ в работу оператору мастером (отмена распределения).

    Перевод программы в статус CREATED. Отмена возможна только для программ со статусом ASSIGNED.

    # TODO после реализации основного процесса
    """
    return ServerNotImplementedError
