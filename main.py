import uvicorn
from sigma_handlers.sigma_db import get_sigma_data
import datetime
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from sigma_handlers.sigma_db import get_sigma_data, get_sigma_data_async
from utils.excel_utils import create_excel, create_excel_async
from datetime import date

app = FastAPI()


# TODO
#  аутентификация авторизация средствами FastAPI
#  словарь настроек форматирования xlsx
#  UI FRONT? Попробовать сделать простой на VUE.js 3
#  cmd (bash) script по развёртке на приложения на клиенте
#  запуск с ярлыка на 0.0.0.0 (совместно с FRONT?) лучше запускать на том же сервере, что и sigma
#  раздача ссылок заинтересованным


# TODO разложить enodpoints по своим местам
@app.get("/download_excel", response_class=StreamingResponse, tags=["Excel"])
async def download_excel(
        start_date: date = Query(...,
                                 description="Начальная дата фильтрации данных (формат: YYYY-MM-DD)",
                                 example="2025-01-09"),
        end_date: date = Query(...,
                               description="Конечная дата фильтрации данных (формат: YYYY-MM-DD)",
                               example="2025-01-20")
) -> StreamingResponse:
    """
    Эндпоинт для генерации Excel-файла на основе данных с фильтрацией по диапазону дат.

    Этот эндпоинт принимает два параметра — `start_date` и `end_date`, которые определяют
    диапазон дат для фильтрации данных. После этого создаётся Excel-файл, содержащий только
    те строки, которые попадают в заданный диапазон.

    **Параметры:**
    - `start_date`: Дата начала периода, начиная с которой данные будут включены в файл.
      Формат: `YYYY-MM-DD`.
    - `end_date`: Дата окончания периода, до которой данные будут включены в файл.
      Формат: `YYYY-MM-DD`.

    **Пример запроса:**
    ```
    GET /download_excel?start_date=2025-01-09&end_date=2025-01-09
    ```

    **Пример ответа:**
    Ответом будет файл Excel с отфильтрованными данными в виде потока. Он будет доступен для скачивания
    с названием, включающим указанные даты.

    :param start_date: Начальная дата для фильтрации данных.
    :param end_date: Конечная дата для фильтрации данных.
    :return: Excel-файл в виде потока с отфильтрованными данными.
    """
    data = await get_sigma_data_async(start_date=start_date, end_date=end_date)
    # Генерация Excel-файла
    file_stream = await create_excel_async(data)
    # Возвращение потока
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=result.xlsx"}
    )


@app.get("/get_raw_data", tags=["Data"])
async def get_raw_data(
        start_date: date = Query(...,
                                 description="Начальная дата фильтрации данных (формат: YYYY-MM-DD)",
                                 example="2025-01-09"),
        end_date: date = Query(...,
                               description="Конечная дата фильтрации данных (формат: YYYY-MM-DD)",
                               example="2025-01-20")
) -> list[dict]:
    """
    Эндпоинт для получения данных с фильтрацией по диапазону дат.

    Этот эндпоинт принимает два параметра — `start_date` и `end_date`, которые определяют
    диапазон дат для фильтрации данных.

    **Параметры:**
    - `start_date`: Дата начала периода, начиная с которой данные будут включены в файл.
      Формат: `YYYY-MM-DD`.
    - `end_date`: Дата окончания периода, до которой данные будут включены в файл.
      Формат: `YYYY-MM-DD`.

    **Пример запроса:**
    ```
    GET /get_raw_data?start_date=2025-01-09&end_date=2025-01-09
    ```

    **Пример ответа:**
    `[
  {
    "Деталь": "4S245 OGP-110.012 Bortik 165x140 1",
    "Дата заказа": "2025-02-14T16:37:10",
    "Дата создания заказа": "2025-01-17T14:20:10",
    "Время реза": 68.279721297642,
    "Материал": "S245",
    "Площадь Net": 23100,
    "Вес Net": 0.7253419381668574,
    "Площадь Rect": 23100,
    "Вес Rect": 0.7253419381668574,
    "Количество заказано": 767,
    "Количество выполнено": 98,
    "Количество в работе": 665,
    "Количество осталось": 4,
    "Номер заказа": "Z10(2025)"
  },...
  ]`
    :param start_date: Начальная дата для фильтрации данных.
    :param end_date: Конечная дата для фильтрации данных.
    :return: Список словарей с данными
    """
    data = await get_sigma_data_async(start_date=start_date, end_date=end_date)
    return data


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# uvicorn main:app --host 0.0.0.0 --port 8000  --reload