"""Регистрация роутеров приложения."""
from pathlib import Path

from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse

from config import STATIC_DIR
from auth.users import fastapi_users
from auth.router import router as auth_router
from auth.schemas import UserRead, UserUpdate
from logist.router import router as logist_router
from master.router import router as master_router
from reports.router import router as reports_router
from techman.router import router as techman_router
from operator_worker.router import router as operator_router


def register_routers(app: FastAPI) -> None:
    """Регистрация роутеров приложения."""
    # Корневой роутер
    root_router = APIRouter()

    @root_router.get("/", tags=["root"])
    def home_page() -> dict:
        """Стартовая страница."""
        return {
            "message": "start page",
        }

    @root_router.get("/instruction", tags=["root"])
    def instruction() -> FileResponse:
        """Стартовая страница."""
        file_path = STATIC_DIR / Path("Инструкция Plasma-Report.pdf")
        return FileResponse(file_path, media_type="application/pdf",
                            filename="Инструкция Plasma-Report.pdf")

    app.include_router(root_router, tags=["root"])
    # аутентификация, авторизация
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    # пользователи FastAPI Users
    app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/user", tags=["user"])

    app.include_router(techman_router, prefix="/techman", tags=["techman"])
    app.include_router(master_router, prefix="/master", tags=["master"])
    app.include_router(operator_router, prefix="/operator", tags=["operator"])
    app.include_router(logist_router, prefix="/logist", tags=["logist"])
    app.include_router(reports_router, prefix="/reports", tags=["reports"])
