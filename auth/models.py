"""Модели пользователей."""
from sqlalchemy.orm import Mapped, mapped_column

from auth.enums import UserRoles
from db.database import Base, uniq_string


class User(Base):
    """Модель пользователя."""

    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[uniq_string]
    password: Mapped[str]
    role: Mapped[UserRoles] = mapped_column(default=UserRoles.USER)

    def __repr__(self) -> str:
        """Строковое представление."""
        return f"{self.__class__.__name__}(id={self.id})"
