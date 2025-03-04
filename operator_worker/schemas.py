"""Схемы сервиса operator."""
from pydantic import BaseModel


class SPartDoneByFio(BaseModel):
    """Схема программы с количеством."""

    id: int
    done_by_fio_doer_id: int
