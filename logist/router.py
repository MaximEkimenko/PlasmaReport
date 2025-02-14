"""Сервис логиста."""
from typing import Annotated

from fastapi import Depends, APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import EmptyAnswerError, AlchemyDatabaseError
from techman.dao import PartDAO, ProgramDAO
from logger_config import log
from techman.enums import PartStatus, ProgramStatus
from logist.schemas import SProgramWithQty
from master.schemas import SProgramsStatus
from dependencies.dao_dep import get_session_with_commit, get_session_without_commit

router = APIRouter()


@router.get("/get_programs_for_calculation", tags=["logist"])
async def get_programs_for_calculation(select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                                       # user_data: Annotated[User, Depends(get_current_techman_user)]
                                       ) -> list[dict]:
    """Получение списка программ со статусом ASSIGNED (распределена).

    Для последующей количественной приёмки логистом.
    """
    programs_select_table = ProgramDAO(session=select_session)
    # result = await programs_select_table.find_all(filters=SPrograms(program_status=ProgramStatus.ASSIGNED))
    # programs_to_calculate = [program.to_dict() for program in result]
    programs_to_calculate = await programs_select_table.find_programs_by_statuses(
        [ProgramStatus.ASSIGNED,
         ProgramStatus.DONE],
    )
    if not programs_to_calculate:
        raise EmptyAnswerError(detail="Нет программ для количественной приёмки.")

    return programs_to_calculate


@router.post("/calculate_parts", tags=["logist"])
async def calculate_parts(parts_with_qty: list[SProgramWithQty],
                          select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                          add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
                          # user_data: Annotated[User, Depends(get_current_techman_user)]
                          ) -> dict:
    """Занесение количества принятого логистом.

    На ввод подаётся список словарей вида {"part_id": id детали, "qty_fact": фактически выполненное количество}}

    Пример ввода:

    ```
    [
        {"id": 13, "qty_fact": 3},
        {"id": 14, "qty_fact": 2}
     ]
     ```
    """
    # добавления статуса деталям в зависимости от фактического и ожидаемого количества
    programs_ids = set()
    part_select_table = PartDAO(session=select_session)
    for part in parts_with_qty:
        part_data = await part_select_table.find_one_or_none_by_id(part.id)
        result_status = PartStatus.DONE_PARTIAL if part.qty_fact < part_data.QtyInProcess else PartStatus.DONE_FULL
        part.part_status = result_status
        log.debug("Деталь {part} получила статус {result_status}.", part=part.id, result_status=result_status.value)

        programs_ids.add(part_data.program_id)

    # обновление фактического количества деталей
    try:
        part_update_table = PartDAO(session=add_session)
        await part_update_table.bulk_update(records=parts_with_qty)
    except SQLAlchemyError as e:
        await add_session.rollback()
        log.error("Ошибка при работе с БД.")
        log.exception(e)
        raise AlchemyDatabaseError from e
    else:
        msg = "Фактическое количество деталей успешно занесено в БД."
    log.success(msg)

    # установка статуса программы в зависимости от статуса деталей
    for program_id in programs_ids:
        program_parts = await part_select_table.get_joined_part_data_by_programs_ids_list([program_id])

        parts_statuses = [part["part_status"] for part in program_parts]
        if all(status == PartStatus.DONE_FULL or status == PartStatus.DONE_PARTIAL for status in parts_statuses): # noqa
            program_status = ProgramStatus.DONE
            program_update_table = ProgramDAO(session=add_session)
            await (program_update_table.bulk_update(
                records=[SProgramsStatus(id=program_id, program_status=program_status.value)]))
            log.success("Программа {program_id} получила статус {program_status.}.",
                        program_id=program_id,
                        program_status=program_status.value)
        else:
            log.debug("Статус программы {program_id} не менялся. Не все детали выполнены.", program_id=program_id)
    return {"msg": msg}
