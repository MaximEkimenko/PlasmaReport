"""Перечисления пользователей."""
import enum


class UserRoles(enum.Enum):
    """Роли пользователей."""

    USER = "Пользователь"
    LOGIST = "Логист"
    ADMIN = "Администратор"
    TECHMAN = "Технолог"

    def __str__(self) -> str:
        """Value в строку."""
        return self.value
