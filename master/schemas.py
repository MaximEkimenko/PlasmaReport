"""Схемы сервиса master."""
from pydantic import BaseModel


class SPrograms(BaseModel):
    """Схема для получения списка программ."""

    id: int
