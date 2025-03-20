"""Routers сервиса operator."""
from typing import Annotated

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from auth.users import get_operator_user
from auth.models import User
from techman.dao import PartDAO, ProgramDAO
from logger_config import log
from techman.enums import ProgramStatus
from dependencies.dao_dep import get_session_with_commit, get_session_without_commit
from operator_worker.schemas import SPartDoneByFio

router = APIRouter()


@router.get("/get_my_programs", tags=["operator"])
async def get_my_programs(fio_id: int,
                          select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                          user_data: Annotated[User, Depends(get_operator_user)],  # noqa ARG001
                          ) -> list:
    """Получение всех программ, оператора."""
    program_select_table = ProgramDAO(session=select_session)
    allowed_statuses = (ProgramStatus.ACTIVE, ProgramStatus.ASSIGNED, ProgramStatus.CALCULATING)
    return await program_select_table.get_program_by_fio_id_with_status(fio_id, statuses=allowed_statuses)


@router.get("/start_program", tags=["operator"])
async def start_program(program_id: int,
                        add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
                        user_data: Annotated[User, Depends(get_operator_user)],  # noqa ARG001
                        new_status: ProgramStatus = ProgramStatus.ACTIVE,
                        ) -> dict | None:
    """Запуск программы в работу оператором.

    Пример ввода:
    {program_id: 123, new_status: "в работе"}
    Параметр new_status необязателен. По умолчанию программа переводится в статус "в работе".
    """
    # TODO добавить ednpoint остановки выполнения программы
    # TODO добавить начало отчёта времени от запуска до остановки выполнения программы
    program_update_table = ProgramDAO(session=add_session)
    await program_update_table.update_program_status(program_id=program_id, new_status=new_status)
    return {"msg": f"Статус программы  {program_id} спешно обновлён на {new_status!r}."}


@router.post("/this_is_my_parts", tags=["operator"])
async def this_is_my_parts(fio_parts: dict,
                           add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
                           user_data: Annotated[User, Depends(get_operator_user)],  # noqa ARG001
                           ) -> dict | None:
    """Назначение детали оператору в выполнение, присвоение программе статуса 'количество принимается'.

    Пример ввода:
        `{"program_id": 13, "fio_doer_id": 2,"parts_ids": [1, 2, 3]}`
    """
    # TODO обработать неверный ввод с frontend
    part_update_table = PartDAO(session=add_session)
    parts_to_update = [SPartDoneByFio(id=part_id, done_by_fio_doer_id=fio_parts["fio_doer_id"])
                       for part_id in fio_parts["parts_ids"]]
    result = await part_update_table.bulk_update(parts_to_update)
    if result:
        program_update_table = ProgramDAO(session=add_session)
        await program_update_table.update_program_status(program_id=fio_parts["program_id"],
                                                         new_status=ProgramStatus.CALCULATING)
        log.success("Детали {parts} назначены оператору {operator}. Статус программы {program_id} изменён на {status}.",
                    parts=fio_parts["parts_ids"],
                    operator=fio_parts["fio_doer_id"],
                    program_id=fio_parts["program_id"],
                    status=ProgramStatus.CALCULATING.value)

        return {"msg": f"Детали {fio_parts['parts_ids']} назначены оператору {fio_parts['fio_doer_id']}. "
                       f"Статус программы {fio_parts['program_id']}, изменён на {ProgramStatus.CALCULATING!r}."}
