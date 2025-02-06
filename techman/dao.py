"""DAO сервиса techman."""
from db.base_dao import BaseDAO
from techman.models import WO, Part, Program


class ProgramDAO(BaseDAO):
    """Класс объекта доступа к БД для программы (СЗ)."""

    model = Program


class WoDAO(BaseDAO):
    """Класс объекта доступа к БД для заказа (СЗ)."""

    model = WO


class PartDAO(BaseDAO):
    """Класс объекта доступа к БД для детали (СЗ)."""

    model = Part
