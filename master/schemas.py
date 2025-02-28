"""Схемы сервиса master."""
from pydantic import BaseModel

from master.enums import Jobs
from techman.enums import ProgramStatus


class SProgramsStatus(BaseModel):
    """Схема для получения списка программ по статусу."""

    id: int | None = None
    program_status: str


class SFioDoer(BaseModel):
    """Схема исполнителя."""

    fio_doer: str | None = None
    position: Jobs | None = Jobs.OPERATOR


class SProgramIDWithFios(BaseModel):
    """Схема id программ с fio исполнителя."""

    id: int
    fio_doer_id: list
    program_status: str = ProgramStatus.ASSIGNED.name

