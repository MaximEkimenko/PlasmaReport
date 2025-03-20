"""Схемы сервиса master."""
from pydantic import BaseModel

from master.enums import Jobs
from techman.enums import ProgramStatus, ProgramPriority


class SProgramsStatus(BaseModel):
    """Схема для получения списка программ по статусу."""

    id: int | None = None
    program_status: ProgramStatus | None = None


class SFioDoer(BaseModel):
    """Схема исполнителя."""

    fio_doer: str | None = None
    position: Jobs | None = Jobs.OPERATOR


class SProgramIDWithFios(BaseModel):
    """Схема id программ с fio исполнителя."""

    id: int
    fio_doers_ids: list
    program_status: str = ProgramStatus.ASSIGNED.name
    program_priority: str | None = ProgramPriority.LOW.name


class SProgramWithFioDoer(BaseModel):
    """Схема программ с fio исполнителя."""


class SFioDoerFull(BaseModel):
    """Схема исполнителя."""

    fio_doer: str | None = None
    position: Jobs | None = Jobs.OPERATOR
    user_id: int | None = None

