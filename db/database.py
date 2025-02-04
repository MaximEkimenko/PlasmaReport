"""Настройка sqlalchemy для работы с базой данных."""
import datetime

from typing import Annotated

from sqlalchemy import TIMESTAMP, Integer, func
from sqlalchemy.orm import (
    Mapped,
    DeclarativeBase,
    class_mapper,
    declared_attr,
    mapped_column,
)
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings

database_url = settings.db_url

engine = create_async_engine(url=database_url)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession,
    expire_on_commit=False,
)
uniq_string = Annotated[str, mapped_column(unique=True, nullable=False)]


class Base(AsyncAttrs, DeclarativeBase):
    """Базовый класс моделей."""

    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(),
    )

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        """Автоматическое заполнение имени таблицы."""
        return cls.__name__.lower()

    def to_dict(self) -> dict:
        """Преобразование модели в словарь."""
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}


# def connection(method):
#     async def wrapper(*args, **kwargs):
#         async with async_session_maker() as session:
#             try:
#                 return await method(*args, **kwargs, session=session)
#             except Exception as e:
#                 await session.rollback()
#                 log.error("Ошибка подключения к БД.")
#                 log.exception(e)
#             finally:
#                 await session.close()
#
#     return wrapper
