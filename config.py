from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent
    DB_NAME: str

    @property
    def db_url(self):
        return fr'sqlite+aiosqlite:///{self.BASEDIR}/{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file=f'{BASE_DIR}/.env', case_sensitive=False)


settings = Settings()
BASEDIR = settings.BASEDIR
