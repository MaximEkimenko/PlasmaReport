"""Взаимодействие с БД sigma nest."""
import datetime

from asyncio import get_running_loop
from concurrent.futures import ThreadPoolExecutor

from utils.common_utils import create_sorted_named_cols
from sigma_handlers.database import Database
from sigma_handlers.sql_queries import main_query, column_query


def get_sigma_data(start_date: datetime, end_date: datetime) -> list[dict]:
    """Получение данных из базы sigma nest."""
    params = (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    with Database() as db:
        result = db.fetch_all(main_query, params)
        columns = tuple(db.get_columns())
        results = [dict(zip(columns, row, strict=False)) for row in result]  # значения
        # сортировка и перевод колонок
        return create_sorted_named_cols(results=results, column_names=columns)


async def get_sigma_data_async(start_date: datetime, end_date: datetime) -> list[dict]:
    """Асинхронная версия функции получения данных."""
    loop = get_running_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, get_sigma_data, start_date, end_date)


def get_column_names() -> tuple[tuple, dict]:
    """Получение списка колонок."""
    with Database() as db:
        result = db.fetch_one(column_query)
        columns = db.get_columns()
        results = dict(zip(result, columns, strict=False))
    return tuple(columns), results


if __name__ == "__main__":
    pass
