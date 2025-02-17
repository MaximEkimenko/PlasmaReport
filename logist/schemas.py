"""Схемы сервиса logist."""
from pydantic import BaseModel

from techman.enums import PartStatus


class SProgramWithQty(BaseModel):
    """Схема программы с количеством."""

    id: int
    qty_fact: int
    part_status: PartStatus | None = None


class SStorageCell(BaseModel):
    """Схема ячейки склада."""

    id: int | None = None
    cell_name: str
