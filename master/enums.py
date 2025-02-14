"""Перечисления сервиса Master."""
from enum import StrEnum


class Jobs(StrEnum):
    """Перечисления должностей."""

    MASTER = "мастер"
    OPERATOR = "оператор"
    TEHNOLOG = "технолог"

