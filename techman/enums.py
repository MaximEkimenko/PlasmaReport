"""Перечисления сервиса Techman."""
import enum


class ProgramStatus(enum.Enum):
    """Статусы программы(сменного задания)."""

    CREATED = "создана"  # TODO Unused in MVP назначается автоматически (запросом по расписанию?)
    UNASSIGNED = "не распределена"
    ASSIGNED = "распределена"
    ACTIVE = "в работе"  # TODO Unused in MVP назначает оператор взятием в работу на своём устройстве
    DONE = "выполнена"
    ARCHIVED = "заархивирована"


class WoStatus(enum.Enum):
    """Статусы заказа."""

    CREATED = "создан"
    ACTIVE = "в работе"
    FINISHED = "завершен"


class PartStatus(enum.Enum):
    """Статусы деталей."""

    UNASSIGNED = "не распределена"
    ASSIGNED = "распределена"  # присваивается если Program.status == ASSIGNED
    # присваивается если фактическое количество детали не совпадает с PIP
    DONE_PARTIAL = "выполнена частично"
    # присваивается если фактическое количество детали совпадает с PIP
    DONE_FULL = "выполнена полностью"
