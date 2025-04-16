"""Конфигурация приложения."""
from typing import ClassVar
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки, переменные окружения приложения."""

    BASE_DIR: ClassVar = Path(__file__).parent
    DB_NAME: str
    sigma_server: str
    sigma_database: str
    sigma_username: str
    sigma_password: str
    SECRET_KEY: str
    ALGORITHM: str

    @property
    def db_url(self) -> str:
        """URL БД приложения."""
        return rf"sqlite+aiosqlite:///{self.BASE_DIR}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env", case_sensitive=False)


settings = Settings()
db_url = settings.db_url
BASEDIR = settings.BASE_DIR
PARTS_DIR = Path(r"M:\Xranenie\Sigma\Parts")
REPORTS_DIR = Path(r"M:\Xranenie\Sigma\eReports")
STATIC_IMAGES_DIR = BASEDIR / "static" / "images"
