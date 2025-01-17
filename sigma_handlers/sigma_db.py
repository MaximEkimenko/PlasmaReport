import datetime
from pprint import pprint
from sigma_handlers.database import Database
from sigma_handlers.SQLqueries import main_query, column_query


def get_sigma_data(start_date: datetime, end_date: datetime) -> list[dict]:
    """Получение данных из базы sigma nest"""
    params = (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    with Database() as db:
        result = db.fetch_all(main_query, params)
        columns = db.get_columns()
        results = [dict(zip(columns, row)) for row in result]  # значения

    return results


def get_column_names() -> tuple[tuple, dict]:
    """Получение списка колонок"""
    with Database() as db:
        result = db.fetch_one(column_query)
        columns = db.get_columns()
        results = dict(zip(result, columns))
    return tuple(columns), results


if __name__ == '__main__':
    # res = get_sigma_data()
    _columns = get_column_names()
    print(_columns)
    # print(res)
    # print(res[0])
