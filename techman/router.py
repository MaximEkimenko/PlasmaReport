"""Techman endpoints."""
import datetime

from typing import Any, Annotated
from datetime import date

from fastapi import Query, Depends, APIRouter
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import InvalidSigmaData, AlchemyDatabaseError
from techman.dao import WoDAO, PartDAO, ProgramDAO
from logger_config import log
from techman.enums import ProgramStatus
from techman.utils import create_data_to_db
from techman.schemas import SWoData, SProgramData, SPartDataPlasmaReport
from dependencies.dao_dep import get_session_with_commit, get_session_without_commit
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
        # user_data: Annotated[User, Depends(get_current_techman_user)],
        select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
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
    programs_table = ProgramDAO(session=select_session)
    # программы с sigma за период
    sigma_programs = await get_program_names(start_date, end_date)
    # имена программ sigma
    sigma_program_names = [program_name["ProgramName"] for program_name in sigma_programs]
    # существующие программы в БД
    existing_programs = await programs_table.get_programs_by_names(sigma_program_names)
    # имена существующих программ в БД
    existing_program_names = [program_name["ProgramName"] for program_name in existing_programs]
    # присвоение статуса новым программа
    new_programs = [
        {
            "ProgramName": program_name["ProgramName"], "status": ProgramStatus.NEW,
        }
        for program_name in sigma_programs if program_name["ProgramName"] not in existing_program_names
    ]
    # только нераспределённые и созданные программы
    allowed_status = (ProgramStatus.UNASSIGNED, ProgramStatus.CREATED)
    existing_programs = [
        {
            "ProgramName": program_name["ProgramName"], "program_status":
            program_name["program_status"],
        }
        for program_name in existing_programs if program_name["program_status"] in allowed_status
    ]

    return new_programs + existing_programs


# TODO промежуточный enopoint с которым пользователь не взаимодействует?
@router.post("/get_parts", tags=["techman", "sigma"],
             response_model=list[dict[str, str | datetime.datetime]])
async def get_active_parts_data(active_programs: list[str],
                                ) -> list[dict[str, str | Any]]:
    """Эндпоинт получения данных по активным программам из таблицы sigma Program вместе с данными заказов - wo.

    Пример ввода:
    `["SP SS- 1-142211", "SP- 3-142202", "SP RIFL- 4-136491", "S390-20-134553"]`
    """
    return await get_parts_data_by_programs(active_programs)


@router.post("/create_data", tags=["techman"])
async def create_data(active_programs: list[str],
                      add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
                      # user_data: Annotated[User, Depends(get_current_techman_user)]
                      ) -> dict:
    """Заполнение БД PlasmaReport данными деталей в работе из sigma nest.

    Пример ввода:
    `["SP SS- 1-142211", "SP- 3-142202", "SP RIFL- 4-136491", "S390-20-134553"]`
    """
    # проверка статусов ввода

    # TODO!!!

    # данные из sigma_nest
    data = await create_data_to_db(active_programs)
    try:
        wos = [SWoData(**wo).model_dump() for wo in data["wos"]]  # валидация wo
        programs = [SProgramData(**program).model_dump() for program in data["programs"]]  # валидация program
    except ValidationError as e:
        log.error("Ошибка валидации данных.")
        log.exception(e)
        raise InvalidSigmaData from e

    # добавление новых данных
    add_parts_table = PartDAO(session=add_session)
    add_programs_table = ProgramDAO(session=add_session)
    add_wos_table = WoDAO(session=add_session)

    # запись новых  данных в БД
    try:
        # Начало транзакции
        async with add_session.begin():
            # Step 1: Вставка данных в таблицу wos и получение ID через RETURNING
            wo_mapping = await add_wos_table.insert_returning(wos)
            # Step 2: Вставка данных в таблицу programs и получение ID через RETURNING
            program_mapping = await add_programs_table.insert_returning(programs)
            # Step 3: Подготовка данных для таблицы parts с добавлением wo_id и program_id
            parts_data = data["parts"]
            parts_with_ids = [
                SPartDataPlasmaReport(
                    **{
                        **part,
                        "wo_number_id": wo_mapping.get(part["WONumber"]),
                        "program_id": program_mapping.get(part["ProgramName"]),
                    },
                )
                for part in parts_data
            ]
            # Step 4: Вставка данных в таблицу parts
            await add_parts_table.add_many(parts_with_ids)
    except Exception as e:
        # При возникновении ошибки выполняется rollback
        await add_session.rollback()
        log.error("Ошибка записи в БД.")
        log.exception(e)
        raise AlchemyDatabaseError from e
    else:
        log.success("Успешная запись в БД.")
        success_msg = {"message": "Данные успешно записаны в БД."}
    # обновление данных

    return success_msg


@router.get("/get_orders", tags=["techman", "sigma"])
async def get_wos(start_date: Annotated[date, Query(..., description="Начальная дата создания",
                                                    example="2025-02-01")],
                  end_date: Annotated[date, Query(..., description="Конечная дата создания",
                                                  example="2025-02-28")],
                  # user_data: Annotated[User, Depends(get_current_techman_user)]
                  ) -> list[dict]:
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
                       # user_data: Annotated[User, Depends(get_current_techman_user)]
                       ) -> list[dict[str, Any]]:
    """Эндпоинт получения данных по конкретному `wo_number` заказу из таблицы sigma WO."""
    return await get_parts_by_wo(wo_number)


@router.get("/get_program_parts/{program_name}", tags=["techman", "sigma"])
async def get_program_parts(program_name: str,
                            # user_data: Annotated[User, Depends(get_current_techman_user)]
                            ) -> list[dict[str, Any]]:
    """Эндпоинт получения данных по конкретной `program_name` программе из таблицы sigma Program.

    Пример: `SP SS- 1-142724`.
    """
    return await get_parts_by_program(program_name)
