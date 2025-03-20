"""Модели пользователей."""
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship, mapped_column
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTable

from auth.enums import UserRole
from db.database import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from techman.models import FioDoer


class User(Base, SQLAlchemyBaseUserTable):
    """Модель пользователя FastApi Users."""

    first_name: Mapped[str]
    last_name: Mapped[str]
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)

    fio_doer: Mapped["FioDoer"] = relationship(back_populates="user")

    @classmethod
    def get_db(cls, session: "AsyncSession") -> "SQLAlchemyUserDatabase":
        """Получить базу данных пользователей."""
        return SQLAlchemyUserDatabase(session, cls)

    def __str__(self) -> str:
        """Строковое представление для админ панели."""
        return self.__class__.__name__ + f"({self.first_name} {self.last_name})"
