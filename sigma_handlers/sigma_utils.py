"""Утилиты для работы с БД sigma nest."""

from asyncio import get_running_loop
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

# from utils.common_utils import create_sorted_named_cols
from sigma_handlers.database import Database
from sigma_handlers.sql_queries import create_placeholders_params_query


async def make_async_sigma_request(sync_func: Callable, params: tuple | None = None) -> list[dict]:
    """Запуск sync_func в новом потоке."""
    loop = get_running_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, sync_func, *params)


def get_any_sigma_data(query: str, params: tuple | None = ()) -> list[dict]:
    """Получение данных из базы sigma nest по запросу query."""
    with Database() as db:
        result = db.fetch_all(query, params)
        columns = tuple(db.get_columns())
    return [dict(zip(columns, row, strict=False)) for row in result]


# TODO DEPRECATED
# def get_sigma_data(start_date: datetime, end_date: datetime) -> list[dict]:
#     """Получение данных из базы sigma nest."""
#     params = (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
#     with Database() as db:
#         result = db.fetch_all(main_query, params)
#         columns = tuple(db.get_columns())
#         results = [dict(zip(columns, row, strict=False)) for row in result]  # значения
#         # сортировка и перевод колонок
#     return create_sorted_named_cols(results=results, column_names=columns)
#
#
# async def get_sigma_data_async(start_date: datetime, end_date: datetime) -> list[dict]:
#     """Асинхронная версия функции получения данных."""
#     loop = get_running_loop()
#     with ThreadPoolExecutor() as pool:
#         return await loop.run_in_executor(pool, get_sigma_data, start_date, end_date)


# def get_column_names() -> tuple[tuple, dict]:
#     """Получение списка колонок."""
#     with Database() as db:
#         result = db.fetch_one(column_query)
#         columns = db.get_columns()
#         results = dict(zip(result, columns, strict=False))
#     return tuple(columns), results


def get_full_parts_data_sql(programs: list[str]) -> list[dict]:
    """Создание запроса для получения полных данных по списку программам."""
    placeholders = ", ".join("?" for _ in programs)
    query = create_placeholders_params_query(placeholders)

    with Database() as db:
        params = tuple(programs)
        result = db.fetch_all(query, params)
        columns = tuple(db.get_columns())
    return [dict(zip(columns, row, strict=False)) for row in result]


# [
# "SP SS- 1-142211",
# "SP- 3-142202",
# "SP RIFL- 4-136491",
# "S390-20-134553"
# ]

# ("SP SS- 1-142211", "SP- 3-142202", "SP RIFL- 4-136491", "S390-20-134553")
# ["SP SS- 1-142211", "SP- 3-142202", "SP RIFL- 4-136491", "S390-20-134553"]

