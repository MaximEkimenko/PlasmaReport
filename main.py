"""Запуск приложения учёта СЗ плазменной резки."""
from pathlib import Path
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import BASEDIR
from logger_config import log
from admin_panel.admin import create_admin_panel
from settings.register_routers import register_routers

# TODO
#  переписать to_dict получение данных на to_dict схем pydantic, использовать to_dict в Base только для моделей
#  без join
#  аутентификация авторизация средствами FastAPI
#  словарь перевода полей для отчёта и выгрузок
#  cmd (bash) script по развёртке на приложения на клиенте
#  запуск с ярлыка на 0.0.0.0 (совместно с FRONT?) лучше запускать на том же сервере, что и sigma
#  изучить, добавить в knowledgebase FastAPI-cash FastAPI-profiler добавить в проект при необходимости.
#  добавить ссылки на картинки программ


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:  # noqa ARG001
    """Управление жизненным циклом приложения."""
    log.info("Инициализация приложения...")
    yield
    log.info("Завершение работы приложения...")


app = FastAPI(
    title="Приложение для учёта сменных заданий установок плазменной резки",
    description="there is no description yet.",
    version="0.0.1",
    lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost,"
    "http://192.168.8.163:3000",
    "http://192.168.8.163:5173",
    "http://192.168.8.146:3000"
    "http://192.168.8.146:5173",
    "http://192.168.8.146",
    "http://127.0.0.1:3000",
    "192.168.8.146:3000",
    "192.168.8.146",
    "192.168.8.163:5173",
    "http://192.168.12.38:5173",
    "192.168.12.38:5173",
    "192.168.8.168:5173",
    "http://192.168.8.168:5173",
]

# Добавляем CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешённые домены
    allow_credentials=True,  # Разрешить передачу куки
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Разрешённые HTTP-методы
    allow_headers=["*"],
)

static_path = BASEDIR / Path("static")
app.mount(
    "/static",
    StaticFiles(directory=static_path),
    name="static",
)

# Регистрация роутеров
register_routers(app)

# запуск админ-панели
create_admin_panel(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="192.168.8.163", port=8000, reload=True)

# uvicorn main:app --host 0.0.0.0 --port 8000  --reload
# uvicorn main:app --reload
