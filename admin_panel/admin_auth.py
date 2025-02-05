"""Настройка аутентификации администратора в панели администратора в SQLAdmin."""
from starlette.requests import Request
from sqladmin.authentication import AuthenticationBackend


class AdminAuth(AuthenticationBackend):
    """Класс аутентификации администратора в панели администратора в SQLAdmin."""

    async def login(self, request: Request) -> bool:
        """Метод аутентификации администратора в панели администратора в SQLAdmin."""
        form_data = await request.form()
        # проверка логина и пароля # TODO в реальном приложении нужно проверять логин и пароль в БД пользователя admin
        if form_data.get("password") == "Epass1":
            request.session.update({"token": "secret_token"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        """Метод выхода из системы администратора в панели администратора в SQLAdmin."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """Метод проверки токена аутентификации в панели администратора в SQLAdmin."""
        return request.session.get("token")


# TODO разобраться с тем как работает token в панели администратора в SQLAdmin
authentication_backend = AdminAuth(secret_key="")
