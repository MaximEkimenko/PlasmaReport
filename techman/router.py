"""Techman endpoints."""
# TODO refactor - move to staff to different files, add docs
#  сделать enpoint, который проверить то, что обновилось и вернёт только доступное для обновления.
#  найти решение по возможности назначения USER нескольких ролей с соответствующим  доступом
import datetime

from typing import Any, Annotated
from datetime import date

from fastapi import Query, Depends, APIRouter
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import InvalidSigmaData, AlchemyDatabaseError, WrongProgramStatusError, ExistingDatabaseEntityError
from techman.dao import WoDAO, PartDAO, ProgramDAO
from logger_config import log
from techman.enums import ProgramStatus
from techman.utils import normalize_value, create_data_to_db
from techman.schemas import SWoData, SProgramData, SUpdateProgramData, SPartDataPlasmaReport
from techman.constants import fields_to_compare
from dependencies.dao_dep import get_session_with_commit, get_session_without_commit
from sigma_handlers.sigma_db import (
    get_wo_names,
    get_parts_by_wo,
    get_program_names,
    get_parts_by_program,
)

router = APIRouter()


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


@router.get("/get_programs", tags=["techman"])
async def get_programs(
        start_date: Annotated[date, Query(..., description="Начальная дата создания",
                                          example="2025-02-01")],
        end_date: Annotated[date, Query(..., description="Конечная дата создания",
                                        example="2025-02-28")],
        # user_data: Annotated[User, Depends(get_current_techman_user)],
        select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
) -> list[dict]:
    """Эндпоинт получения списка созданных программ из таблицы sigma Program.

    Этот эндпоинт принимает два параметра — `start_date` и `end_date`, которые определяют
      диапазон дат для фильтрации данных.

      **Параметры:**
      - `start_date`: Дата начала периода, начиная с которой данные будут включены в файл.
        Формат: `YYYY-MM-DD`.
      - `end_date`: Дата окончания периода, до которой данные будут включены в файл.
        Формат: `YYYY-MM-DD`.

      **Пример запроса:**
      GET /programs?start_date=2025-01-09&end_date=2025-01-09
    """
    programs_table = ProgramDAO(session=select_session)
    # программы с sigma за период
    sigma_programs = await get_program_names(start_date, end_date)
    # имена программ sigma
    sigma_program_names = [program_name["ProgramName"] for program_name in sigma_programs]
    # существующие программы в БД
    existing_programs = await programs_table.find_programs_by_names(sigma_program_names)
    # имена существующих программ в БД
    existing_program_names = [program_name["ProgramName"] for program_name in existing_programs]
    # присвоение статуса новым программа
    new_programs = [
        {"program_status": ProgramStatus.NEW } | dict(program_name.items())
        for program_name in sigma_programs
        if program_name["ProgramName"] not in existing_program_names
    ]
    # только нераспределённые и созданные программы разрешены для обновления
    allowed_status = (ProgramStatus.UNASSIGNED, ProgramStatus.CREATED)
    existing_programs = [
        dict(program_name.items())
        for program_name in existing_programs
        if program_name["program_status"] in allowed_status
    ]
    return new_programs + existing_programs

@router.post("/create_data", tags=["techman"])
async def create_data(active_programs: list[dict],
                      add_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
                      select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
                      # user_data: Annotated[User, Depends(get_current_techman_user)]
                      ) -> dict:
    """Заполнение БД PlasmaReport данными деталей в работе из sigma nest.

    На вход подаётся словарь с именем программы и её статусом.
    Данный endpoint обрабатывает только статус = "новая".
    Пример ввода:
    ```
    [
       {
        "program_status": "новая",
        "ProgramName": "SP RIFL-4-143441"
      },
      {
        "program_status": "новая",
        "ProgramName": "GS-4-143411"
      },
      {
        "program_status": "новая",
        "ProgramName": "GS-3-143402"
      }
    ]
      ```
    """
    program_statuses = {program["program_status"] for program in active_programs}
    program_names = [program["ProgramName"] for program in active_programs]
    # проверка статусов ввода
    if program_statuses != {ProgramStatus.NEW}:
        log.error("Неверный статус ввода в перечне статусов: {statuses}", statuses=program_statuses)
        msg = f"Присутствует неверный статус ввода в перечне статусов: {program_statuses}."
        raise WrongProgramStatusError(detail=msg)
    # данные из sigma_nest
    data = await create_data_to_db(program_names)
    try:
        wos = [SWoData(**wo).model_dump() for wo in data["wos"]]  # валидация wo
        programs = [SProgramData(**program).model_dump() for program in data["programs"]]  # валидация program
    except ValidationError as e:
        log.error("Ошибка валидации данных.")
        log.exception(e)
        raise InvalidSigmaData from e

    # dao объекты
    add_parts_table = PartDAO(session=add_session)
    add_programs_table = ProgramDAO(session=add_session)
    add_wos_table = WoDAO(session=add_session)
    select_program_table = ProgramDAO(select_session)
    select_wos_table = WoDAO(select_session)
    # проверка уже заполненных программ
    existing_programs = await select_program_table.find_programs_by_names(program_names)
    existing_programs_numbers = [program_name["ProgramName"] for program_name in existing_programs]
    if existing_programs:
        log.error("Программы уже существуют в БД.")
        msg = f"Программы {existing_programs_numbers} уже существуют в БД."
        raise ExistingDatabaseEntityError(detail=msg)
    # проверка уже заполненных заказов wos
    existing_wos = await select_wos_table.find_wos_by_names([wo["WONumber"] for wo in wos])
    wo_mapping = {}
    if existing_wos:
        existing_wos_names = [wo_name["WONumber"] for wo_name in existing_wos]
        # удаление уже существующих заказов из списка для добавления в БД
        wos = [item for item in wos if item.get("WONumber") not in existing_wos_names]
        # данные для вноса FK wo_number
        wo_mapping.update({wo["WONumber"]: wo["id"] for wo in existing_wos})
        log.info("Заказы уже {wos} существуют в БД. Удаление их из списка для добавления.", wos=existing_wos_names)

    # запись новых  данных в БД
    try:
        # Начало транзакции
        async with add_session.begin():
            # Вставка данных в таблицу wos и получение ID через RETURNING
            if wos:
                wo_mapping.update(await add_wos_table.insert_returning(wos))
            # Вставка данных в таблицу programs и получение ID через RETURNING
            program_mapping = await add_programs_table.insert_returning(programs)
            # Подготовка данных для таблицы parts с добавлением wo_id и program_id
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
            # Вставка данных в таблицу parts
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

    return success_msg


@router.put("/update_data", tags=["techman"])
async def update_data(
        active_programs: list[SUpdateProgramData],
        update_session: Annotated[AsyncSession, Depends(get_session_with_commit)],
        select_session: Annotated[AsyncSession, Depends(get_session_without_commit)],
        # user_data: Annotated[User, Depends(get_current_techman_user)]
) -> dict:
    """Обновление БД PlasmaReport данными деталей в работе из sigma nest.

    На вход подаётся словарь с именем программы и её статусом.
    Данный endpoint обрабатывает только статусы = "создана" и "не распределена".
    Пример минимально необходимого ввода (остальные поля игнорируются):
    ```
    [
        {
            "program_status": "создана",
            "ProgramName": "SP RIFL-4-143441",
            "id": 3
        },
        {
            "program_status": "создана",
            "ProgramName": "GS-4-143411",
            "id": 2
        },
        {
            "program_status": "создана",
            "ProgramName": "GS-3-143402",
            "id": 1
        }
    ]
      ```
    """
    # проверка статусов ввода
    # TODO обработать статусы отдельным запросом
    program_statuses = {
        program.program_status for program in active_programs
        if program.program_status not in (ProgramStatus.CREATED, ProgramStatus.UNASSIGNED)
    }
    if program_statuses:
        log.error("Неверный статус ввода в перечне статусов: {statuses}", statuses=program_statuses)
        msg = f"Присутствует неверный статус ввода в перечне статусов: {program_statuses}."
        raise WrongProgramStatusError(detail=msg)

    # обновление данных
    part_table_select = PartDAO(select_session)  # объект DAO
    program_names = [program.ProgramName for program in active_programs]  # имена программ
    program_ids = [program.id for program in active_programs]  # id программ
    # новые детали:
    sigma_data = await create_data_to_db(program_names)
    sigma_parts = sigma_data["parts"]
    # существующие детали
    existing_parts = await part_table_select.get_parts_by_program_ids(program_ids)

    # список полей, для учёта в сравнении

    # словарь сопоставления ProgramName и program_id
    id_program_name_dict = {
        program.id: program.ProgramName
        for program in active_programs
    }

    # словари с ключом (ProgramName, program_id) для сравнения
    existing_parts_dict = {
        (part["PartName"], id_program_name_dict[part["program_id"]]): part for part in existing_parts
        # (part["PartName"], part["program_id"]): part for part in existing_parts
    }
    sigma_parts_dict = {
        (part["PartName"], part["ProgramName"]): part for part in sigma_parts
        # (part["PartName"], part["WONumber"]): part for part in sigma_parts
    }

    # изменённые элементы
    changed_elements = []
    for key, sigma_part in sigma_parts_dict.items():
        if key in existing_parts_dict:
            existing_part = existing_parts_dict[key]
            differences = {
                field: (normalize_value(existing_part.get(field)), normalize_value(sigma_part.get(field)))
                for field in fields_to_compare
                if normalize_value(existing_part.get(key)) != normalize_value(sigma_part.get(key))
            }
            if differences:
                changed_elements.append({
                    "ProgramName": sigma_part["ProgramName"],
                    "changes": differences,
                })

    # Обновление изменённых элементов
    part_update_table = PartDAO(session=update_session)
    if changed_elements:
        await part_update_table.bulk_update_by_field_name(records=changed_elements, update_field_name="ProgramName")
        update_message = ("\n".join(
            [
                f"Для программы {item['ProgramName']}, Изменения: {item['changes']} обновлены в БД."
                for item in changed_elements
            ],
        ))
    else:
        update_message = "Изменений для обновления в программах нет."
    log.info(update_message)

    # добавленные элементы
    added_elements = [
        part for key, part in sigma_parts_dict.items() if key not in existing_parts_dict
    ]
    # добавление новых элементов
    if added_elements:
        wo_select_table = WoDAO(select_session)
        program_select_table = ProgramDAO(select_session)

        for element in added_elements:
            program = await program_select_table.find_programs_by_names([element["ProgramName"]])
            program_id = program[0]["id"]
            wo = await wo_select_table.find_wos_by_names([element["WONumber"]])
            wo_number_id = wo[0]["id"]
            element.update({"program_id": program_id, "wo_number_id": wo_number_id})

        pydentic_elements_to_add = [SPartDataPlasmaReport(**element) for element in added_elements]
        await part_update_table.add_many(pydentic_elements_to_add)
        added_message = ("\n".join(
            [
                f"Детали {item} добавлены в БД."
                for item in added_elements
            ],
        ))
    else:
        added_message = "Деталей для добавления при обновлении программы нет."
    log.info(added_message)

    # удалённые элементы
    removed_elements = [
        part for key, part in existing_parts_dict.items() if key not in sigma_parts_dict
    ]
    # удаление элементов
    if removed_elements:
        for element in removed_elements:
            await part_update_table.delete_by_id(element_id=element["id"])
        delete_message = ("\n".join(
            [
                f"Детали {item} удалены из БД."
                for item in added_elements
            ],
        ))
    else:
        delete_message = "Деталей для добавления при обновлении программы нет."
    log.info(delete_message)

    return {
        "msg": "ok",
        "changed_elements": changed_elements,
        "added_elements": added_elements,
        "removed_elements": removed_elements,
    }

# TODO промежуточный enopoint с которым пользователь не взаимодействует?
# @router.post("/get_parts", tags=["techman", "sigma"],
#              response_model=list[dict[str, str | datetime.datetime]])
# async def get_active_parts_data(active_programs: list[str],
#                                 ) -> list[dict[str, str | Any]]:
#     """Эндпоинт получения данных по активным программам из таблицы sigma Program вместе с данными заказов - wo.
#
#     ВСПОМОГАТЛЕЛЬНЫЙ endpoint
#     Пример ввода:
#     `["SP SS- 1-142211", "SP- 3-142202", "SP RIFL- 4-136491", "S390-20-134553"]`
#     """
#     return await get_parts_data_by_programs(active_programs)
