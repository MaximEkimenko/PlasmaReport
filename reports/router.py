"""Сервис для работы с отчетами."""
from typing import Annotated
from datetime import date

from fastapi import Query, Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import EmptyAnswerError
from reports.dao import ReportPartDAO
from dependencies.dao_dep import get_session_without_commit
from settings.translate_dict import get_translated_keys
from sigma_handlers.sigma_db import get_parts_info_by_wo

router = APIRouter()


@router.get("/parts_full", tags=["reports"])
async def get_full_parts_report(
        start_date: Annotated[date, Query(..., description="Начальная дата отчёта",
                                          example="2025-02-01")],
        end_date: Annotated[date, Query(..., description="Конечная дата отчёта",
                                        example="2025-02-28")],
        # user_data: Annotated[User, Depends(get_current_techman_user)],
        select_session: Annotated[AsyncSession, Depends(get_session_without_commit)]) -> dict:
    """Получение полного отчёта по деталям."""
    parts_select_table = ReportPartDAO(session=select_session)
    parts = await parts_select_table.get_full_part_data_start_end(start_date=start_date, end_date=end_date)
    if not parts:
        raise EmptyAnswerError(detail="Нет деталей для отчёта в этом интервале времени.")

    headers = get_translated_keys(parts)

    return {"data": parts, "headers": headers}


@router.get("/get_wo_details", tags=["reports"])
async def get_wo_details(wo_number: str,
                         # user_data: Annotated[User, Depends(get_techman_user)
                         ) -> dict:
    """Получение деталей заказа.

    На вход подаётся строка имени заказа (wo_number).
    Пример ввода:
    ```1277 890WH-2G-GOF```
    """
    parts = await get_parts_info_by_wo(wo_number)
    headers = get_translated_keys(parts)
    return {"data": parts, "headers": headers}
