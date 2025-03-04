"""Перечисления сервиса Techman."""
import enum


class ProgramStatus(enum.StrEnum):
    """Статусы программы(сменного задания)."""

    NEW = "новая"
    CREATED = "создана"
    UNASSIGNED = "не распределена"
    ASSIGNED = "распределена"
    ACTIVE = "в работе"
    CALCULATING = "количество принимается"
    DONE = "выполнена"


class PartStatus(enum.StrEnum):
    """Статусы деталей."""

    UNASSIGNED = "не распределена"
    ASSIGNED = "распределена"  # присваивается если Program.status == ASSIGNED
    # присваивается если фактическое количество детали не совпадает с PIP
    DONE_PARTIAL = "выполнена частично"
    # присваивается если фактическое количество детали совпадает с PIP
    DONE_FULL = "выполнена полностью"
    # ACCEPTED = "принята"


class WoStatus(enum.StrEnum):
    """Статусы заказа."""

    CREATED = "создан"
    ACTIVE = "в работе"
    FINISHED = "завершен"




class ProgramPriority(enum.StrEnum):
    """Приоритеты программы(сменного задания)."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
