"""Перечисления пользователей."""
import enum


class UserRole(enum.Enum):
    """Роли пользователей."""

    USER = "Пользователь"
    LOGIST = "Логист"
    ADMIN = "Администратор"
    TECHMAN = "Технолог"
    MASTER = "Мастер"

    def __str__(self) -> str:
        """Value в строку."""
        return self.value
