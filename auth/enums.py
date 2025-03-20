"""Перечисления пользователей."""
import enum


class UserRole(enum.Enum):
    """Роли пользователей."""

    USER = "Пользователь"
    ADMIN = "Администратор"
    TECHMAN = "Технолог"
    MASTER = "Мастер"
    OPERATOR = "Оператор"
    LOGIST = "Логист"

    def __str__(self) -> str:
        """Value в строку."""
        return self.value
