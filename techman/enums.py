"""Перечисления сервиса Techman."""
import enum


class ProgramStatus(enum.StrEnum):
    """Статусы программы(сменного задания)."""

    NEW = "новая"
    CREATED = "создана"
    UNASSIGNED = "не распределена"  # TODO not used ?
    ASSIGNED = "распределена"
    ACTIVE = "в работе"  # TODO Unused in MVP назначает оператор взятием в работу на своём устройстве
    DONE = "выполнена"
    ARCHIVED = "заархивирована"


class WoStatus(enum.StrEnum):
    """Статусы заказа."""

    CREATED = "создан"
    ACTIVE = "в работе"
    FINISHED = "завершен"


class PartStatus(enum.StrEnum):
    """Статусы деталей."""

    UNASSIGNED = "не распределена"
    ASSIGNED = "распределена"  # присваивается если Program.status == ASSIGNED
    # присваивается если фактическое количество детали не совпадает с PIP
    DONE_PARTIAL = "выполнена частично"
    # присваивается если фактическое количество детали совпадает с PIP
    DONE_FULL = "выполнена полностью"

class ProgramPriority(enum.IntEnum):
    """Приоритеты программы(сменного задания)."""

    LOW = 4
    MEDIUM = 3
    HIGH = 2
    CRITICAL = 1
