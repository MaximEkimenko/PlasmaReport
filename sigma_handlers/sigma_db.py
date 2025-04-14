"""Взаимодействие с БД sigma nest."""
from datetime import date

from sigma_handlers.sigma_utils import get_any_sigma_data, get_full_parts_data_sql, make_async_sigma_request
from sigma_handlers.sql_queries import (
    parts_by_wo_query,
    work_orders_query,
    programs_name_query,
    parts_by_program_query,
    single_date_programs_name_query,
)


async def get_program_names(start_date: date, end_date: date) -> list[dict]:
    """Получение списка созданных программ sigma nest программ."""
    functions_params = (
        programs_name_query,
        (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
    )
    return await make_async_sigma_request(get_any_sigma_data, functions_params)


async def single_date_get_program_names(start_date: date) -> list[dict]:
    """Получение списка созданных программ sigma nest программ."""
    functions_params = (
        single_date_programs_name_query,
        (start_date.strftime("%Y-%m-%d")),
    )
    return await make_async_sigma_request(get_any_sigma_data, functions_params)


async def get_wo_names(start_date: date, end_date: date) -> list[dict]:
    """Получение списка заказов."""
    functions_params = (
        work_orders_query,
        (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
    )
    return await make_async_sigma_request(get_any_sigma_data, functions_params)


async def get_parts_by_program(program_name: str) -> list[dict]:
    """Получение деталей программы."""
    function_params = (
        parts_by_program_query,
        (program_name,),
    )
    return await make_async_sigma_request(get_any_sigma_data, function_params)


async def get_parts_by_wo(wo_name: str) -> list[dict]:
    """Получение деталей заказа."""
    function_params = (
        parts_by_wo_query,
        (wo_name,),
    )
    return await make_async_sigma_request(get_any_sigma_data, function_params)


async def get_parts_data_by_programs(programs: list[str]) -> list[dict]:
    """Получение полной информации с деталями по списку программ."""
    return await make_async_sigma_request(get_full_parts_data_sql, (programs, ))


if __name__ == "__main__":

    pass


