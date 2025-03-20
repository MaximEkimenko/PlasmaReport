"""FastAPI Users User Manager."""

from collections.abc import AsyncGenerator

from fastapi import Depends, Request, Response
from fastapi_users import FastAPIUsers, IntegerIDMixin, BaseUserManager, models
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users.authentication import (
    JWTStrategy,
    AuthenticationBackend,
)

from config import settings
from exceptions import ForbiddenException
from master.dao import FioDoerDAO
from auth.models import User
from db.database import async_session_maker
from logger_config import log
from master.schemas import SFioDoerFull
from settings.constants import AUTH_LIFETIME_SECONDS
from dependencies.auth_dep import get_user_db

from .enums import UserRole
from .transport import bearer_transport

SECRET = settings.SECRET_KEY


class UserManager(IntegerIDMixin, BaseUserManager):
    """Менеджер пользователей FastAPI Users."""

    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Request | None = None) -> None:  # noqa  ARG002
        """Вызывается после регистрации пользователя."""
        # добавление исполнителя в таблицу fio_doer
        if str(user.role).lower() == UserRole.OPERATOR.value.lower():
            async with async_session_maker() as session:
                add_fio_doer = FioDoerDAO(session=session)
                to_add = SFioDoerFull(user_id=user.id, fio_doer=f"{user.first_name} {user.last_name}")
                await add_fio_doer.add(to_add)
                await session.commit()

    async def on_after_forgot_password(
            self, user: User, token: str, request: Request | None = None,  # noqa  ARG002
    ) -> None:
        """Вызывается после запроса на сброс пароля пользователя."""
        log.info("Пользователь {user_id} забыл свой пароль. Токен сброса пароля: {token}",
                 user_id=user.id, token=token)

    async def on_after_request_verify(
            self, user: User, token: str, request: Request | None = None,  # noqa  ARG002
    ) -> None:
        """Вызывается после запроса на верификацию пользователя."""
        log.info("Верификация пользователя {user_id} запрошена для пользователя {user_id}. "
                 "Токен верификации token: {token}", user_id=user.id, token=token)

    async def on_after_login(
            self,
            user: User,
            request: Request | None = None, # noqa  ARG002
            response: Response | None = None,  # noqa  ARG002
    ) -> None:
        """Вызывается после успешного входа пользователя."""
        log.info("Пользователь {user_id} вошёл в систему.", user_id=user.id)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)) -> AsyncGenerator:
    """Получение менеджера пользователей FastAPI Users."""
    yield UserManager(user_db)


# стратегия для аутентификации по токену JWT
def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    """Получение стратегии FastAPI Users Backend."""
    return JWTStrategy(secret=SECRET, lifetime_seconds=AUTH_LIFETIME_SECONDS)


# auth backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    # transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

# зависимости для аутентификации пользователя
current_active_user = fastapi_users.current_user(active=True)
current_super_user = fastapi_users.current_user(active=True, superuser=True)


async def get_techman_user(current_user: User = Depends(current_active_user)) -> User:
    """Проверяем права пользователя как технолога."""
    allowed_roles = (UserRole.TECHMAN, UserRole.ADMIN)
    if current_user.role in allowed_roles:
        return current_user
    raise ForbiddenException


async def get_master_user(current_user: User = Depends(current_active_user)) -> User:
    """Проверяем права пользователя как мастера."""
    allowed_roles = (UserRole.MASTER, UserRole.ADMIN, UserRole.OPERATOR)
    if current_user.role in allowed_roles:
        return current_user
    raise ForbiddenException


async def get_operator_user(current_user: User = Depends(current_active_user)) -> User:
    """Проверяем права пользователя как оператора."""
    allowed_roles = (UserRole.OPERATOR.value.lower(), UserRole.ADMIN.value.lower(), UserRole.MASTER.value.lower())
    if current_user.role.value.lower() in allowed_roles:
        return current_user
    raise ForbiddenException


async def get_logist_user(current_user: User = Depends(current_active_user)) -> User:
    """Проверяем права пользователя как логиста."""
    allowed_roles = (UserRole.LOGIST, UserRole.ADMIN, UserRole.MASTER)
    if current_user.role in allowed_roles:
        return current_user
    raise ForbiddenException
