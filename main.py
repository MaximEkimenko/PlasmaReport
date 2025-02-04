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
from settings.register_routers import register_routers

# TODO
#  аутентификация авторизация средствами FastAPI
#  словарь настроек форматирования xlsx
#  UI FRONT? Попробовать сделать простой на VUE.js 3
#  cmd (bash) script по развёртке на приложения на клиенте
#  запуск с ярлыка на 0.0.0.0 (совместно с FRONT?) лучше запускать на том же сервере, что и sigma
#  раздача ссылок заинтересованным


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[dict, None]:  # noqa ARG001
    """Управление жизненным циклом приложения."""
    log.info("Инициализация приложения...")
    yield
    log.info("Завершение работы приложения...")


app = FastAPI(
    title="Приложение для учёта сменных заданий усановок пламзенной резки",
    description="there is no description yet.",
    version="0.0.1",
    lifespan=lifespan )

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.8.163:3000",
]

# Добавляем CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Разрешённые домены
    allow_credentials=True,  # Разрешить передачу куки
    allow_methods=["*"],  # Разрешённые HTTP-методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешённые заголовки (Authorization и др.)
)

static_path = BASEDIR / Path("static")
app.mount(
    "/static",
    StaticFiles(directory=static_path),
    name="static",
)

# Регистрация роутеров
register_routers(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="192.168.8.163", port=8000, reload=True)

# uvicorn main:app --host 0.0.0.0 --port 8000  --reload
# uvicorn main:app --reload
