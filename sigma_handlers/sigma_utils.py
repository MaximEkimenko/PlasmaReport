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


def get_full_parts_data_sql(programs: list[str]) -> list[dict]:
    """Создание запроса для получения полных данных по списку программам."""
    placeholders = ", ".join("?" for _ in programs)
    query = create_placeholders_params_query(placeholders)

    with Database() as db:
        params = tuple(programs)
        result = db.fetch_all(query, params)
        columns = tuple(db.get_columns())
    return [dict(zip(columns, row, strict=False)) for row in result]
