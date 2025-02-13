"""Routers сервиса master."""

from typing import Annotated

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from techman.dao import PartDAO, ProgramDAO
from master.schemas import SPrograms
from dependencies.dao_dep import get_session_without_commit

router = APIRouter()


@router.post("/get_programs_for_assignment", tags=["master"])
async def get_programs_for_assignment(program_ids: list[int],
                                      # add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
                                      select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                                      # user_data: Annotated[User, Depends(get_current_techman_user)]
                                      ) -> dict:
    """Получение списка программ со статусом CREATED (создана) для передачи в работу оператору мастером.

    Перевод программы в статус ASSIGNED.

    Пример ввода [1, 2, 3, 4]
    """
    # TODO проверка статусов программы
    programs_select_table = ProgramDAO(session=select_session)

    # programs = await programs_select_table.find_one_or_none(filters=SPrograms(id=1))
    programs = await programs_select_table.find_all(filters=SPrograms(id=program_ids))
    # print(programs)
    return {"programs": [program.to_dict() for program in programs]}
    # return {"programs": programs.to_dict()}


@router.post("/assign_program", tags=["master"])
async def assign_program(program_ids: list[int],
                         # add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
                         select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                         # user_data: Annotated[User, Depends(get_current_techman_user)]
                         ) -> dict:
    """Передача программ в работу оператору мастером. Перевод программы в статус ASSIGNED."""
    """Пример ввода [1, 2, 3, 4]"""
    program_select_table = PartDAO(session=select_session)
    # TODO проверка статусов программы

    # schemas = [SUpdateProgramData(id=program_id) for program_id in program_ids]

    parts = await program_select_table.get_parts_by_program_ids(program_ids)

    # programs = [program.to_dict() for program in result]

    return {"ans": parts}
