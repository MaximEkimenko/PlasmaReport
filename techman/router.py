"""Techman endpoints."""
import datetime

from typing import Annotated
from datetime import date

from fastapi import Query, Depends, APIRouter

from auth.models import User
from dependencies.auth_dep import get_current_techman_user
from sigma_handlers.sigma_db import (
    get_wo_names,
    get_parts_by_wo,
    get_program_names,
    get_parts_by_program,
    get_parts_data_by_programs,
)

router = APIRouter()

# TODO  найти решение по возможности назначения USER нескольких ролей с соответствующим  доступом


# response_class = ...
@router.get("/get_programs", tags=["techman", "sigma"])
async def get_programs(
        start_date: Annotated[date, Query(..., description="Начальная дата создания",
                                          example="2025-02-01")],
        end_date: Annotated[date, Query(..., description="Конечная дата создания",
                                        example="2025-02-28")],
        user_data: Annotated[User, Depends(get_current_techman_user)] # noqa
) -> list[dict[str, str]]:
    """Эндпоинт получения списка созданных программ из таблицы sigma Program.

    Этот эндпоинт принимает два параметра — `start_date` и `end_date`, которые определяют
      диапазон дат для фильтрации данных.

      **Параметры:**
      - `start_date`: Дата начала периода, начиная с которой данные будут включены в файл.
        Формат: `YYYY-MM-DD`.
      - `end_date`: Дата окончания периода, до которой данные будут включены в файл.
        Формат: `YYYY-MM-DD`.

      **Пример запроса:**
      ```
      GET /programs?start_date=2025-01-09&end_date=2025-01-09
    """
    return await get_program_names(start_date, end_date)


# TODO промежуточный enopoint с которым пользователь не взаимодействует?
@router.post("/get_parts", tags=["techman", "sigma"],
             response_model=list[dict[str, str | datetime.datetime]])
async def get_active_parts_data(active_programs: list[str]) -> list[dict[str, str | datetime.datetime]]:
    """Эндпоинт получения данных по активным программам из таблицы sigma Program вместе с данными заказов - wo.

    Пример ввода:
    `["SP SS- 1-142211", "SP- 3-142202", "SP RIFL- 4-136491", "S390-20-134553"]`
    """
    return await get_parts_data_by_programs(active_programs)


@router.post("/create_data", tags=["techman"])
async def create_data(active_programs: list[str]) -> None:
    """Заполнение БД PlasmaReport данными деталей в работе из sigma nest.

    Пример ввода:
    `["SP SS- 1-142211", "SP- 3-142202", "SP RIFL- 4-136491", "S390-20-134553"]`
    """
    # data = await create_data_to_db(active_programs)
    # programs = data["programs"]
    # wos = data["wos"]
    # parts = data["parts"]







@router.get("/get_orders", tags=["techman", "sigma"],
            response_model=list[dict[str, str | datetime.datetime]])
async def get_wos(start_date: Annotated[date, Query(..., description="Начальная дата создания",
                                                    example="2025-02-01")],
                  end_date: Annotated[date, Query(..., description="Конечная дата создания",
                                                  example="2025-02-28")],
                  user_data: Annotated[User, Depends(get_current_techman_user)]) -> list[dict]:  # noqa
    """Эндпоинт получения списка активных заказов из таблицы sigma WO.

    Этот эндпоинт принимает два параметра — `start_date` и `end_date`, которые определяют
      диапазон дат для фильтрации данных.

      **Параметры:**
      - `start_date`: Дата начала периода, начиная с которой данные будут включены в файл.
        Формат: `YYYY-MM-DD`.
      - `end_date`: Дата окончания периода, до которой данные будут включены в файл.
        Формат: `YYYY-MM-DD`.

      **Пример запроса:**
      ```
      GET /orders?start_date=2025-01-09&end_date=2025-01-09
      ```
    """
    return await get_wo_names(start_date, end_date)


@router.get("/get_order_parts/{wo_number}", tags=["techman", "sigma"],
            response_model=list[dict[str, str | datetime.datetime]])
async def get_wo_parts(wo_number: str,
                 user_data: Annotated[User, Depends(get_current_techman_user)]# noqa
                 ) -> list[dict[str, str | datetime.datetime]]:
    """Эндпоинт получения данных по конкретному `wo_number` заказу из таблицы sigma WO."""
    return await get_parts_by_wo(wo_number)


@router.get("/get_program_parts/{program_name}", tags=["techman", "sigma"],
            response_model=list[dict[str, str | datetime.datetime]])
async def get_program_parts(program_name: str,
                      user_data: Annotated[User, Depends(get_current_techman_user)] # noqa
                      ) -> list[dict[str, str | datetime.datetime]]:
    """Эндпоинт получения данных по конкретной `program_name` программе из таблицы sigma Program."""
    return await get_parts_by_program(program_name)







