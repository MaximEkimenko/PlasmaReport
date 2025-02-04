"""Обработка данных excel."""
import io
import datetime

from asyncio import get_running_loop
from concurrent.futures import ThreadPoolExecutor

from openpyxl import Workbook

from sigma_handlers.sigma_db import get_sigma_data


def create_excel(data: list) -> io.BytesIO:
    """Создание excel файла."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"

    # Заголовки
    headers = list(data[0].keys())
    ws.append(headers)

    # Данные
    for row in data:
        ws.append(
            [
                row[key]
                if not isinstance(row[key], datetime.datetime)
                else row[key].strftime("%d.%m.%Y")
                for key in headers
            ],
        )
    # сохранение в файл
    # filename = "file_result.xlsx"
    # wb.save(filename)
    # Сохранение в поток
    file_stream = io.BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)
    return file_stream


async def create_excel_async(data: list) -> io.BytesIO:
    """Асинхронная обертка функции создания excel файла."""
    loop = get_running_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, create_excel, data)


if __name__ == "__main__":
    start_date = datetime.date(2025, 1, 1)  # дата начала выборки
    end_date = datetime.date(2025, 1, 10)  # дата окончания выборки
    _data = get_sigma_data(start_date, end_date)
    create_excel(_data)
