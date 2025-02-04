"""Регистрация роутеров приложения."""
from fastapi import FastAPI, APIRouter

from auth.router import router as auth_router
from logist.router import router as logist_router


def register_routers(app: FastAPI) -> None:
    """Регистрация роутеров приложения."""
    # Корневой роутер
    root_router = APIRouter()

    @root_router.get("/", tags=["root"])
    def home_page() -> dict:
        """Стартовая страница."""  # TODO перенести в отдельный rout файл
        return {
            "message": "start page",
        }

    # Подключение роутеров
    app.include_router(root_router, tags=["root"])
    app.include_router(logist_router, prefix="/logist", tags=["logist"])
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
