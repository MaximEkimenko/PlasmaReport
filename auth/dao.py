"""DAO сервиса auth."""
from auth.models import User
from db.base_dao import BaseDAO


class UsersDAO(BaseDAO[User]):
    """Класс объекта доступа к БД для пользователя."""

    model = User
