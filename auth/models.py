"""Модели пользователей."""
from sqlalchemy.orm import Mapped, mapped_column

from auth.enums import UserRole
from db.database import Base, uniq_string


class User(Base):
    """Модель пользователя."""

    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[uniq_string]
    password: Mapped[str]
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)

    def __repr__(self) -> str:
        """Строковое представление."""
        return f"{self.__class__.__name__}(id={self.id})"
