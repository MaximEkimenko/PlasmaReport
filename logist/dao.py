"""DAO сервиса logist."""
from auth.models import User
from db.base_dao import BaseDAO


class LogistUsersDAO(BaseDAO):
    """Класс объекта доступа к БД для логиста."""

    model = User

