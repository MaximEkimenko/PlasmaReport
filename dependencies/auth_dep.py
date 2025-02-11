"""FastAPI зависимости для сервиса auth."""

from datetime import UTC, datetime

from jose import JWTError, ExpiredSignatureError, jwt
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from auth.dao import UsersDAO
from auth.enums import UserRole
from exceptions import (
    TokenNoFound,
    NoJwtException,
    NoUserIdException,
    ForbiddenException,
    TokenExpiredException,
    UserNotFoundException,
)
from auth.models import User
from dependencies.dao_dep import get_session_without_commit


def get_access_token(request: Request) -> str:
    """Извлекаем access_token из кук."""
    token = request.cookies.get("user_access_token")
    if not token:
        raise TokenNoFound
    return token


def get_refresh_token(request: Request) -> str:
    """Извлекаем refresh_token из кук."""
    token = request.cookies.get("user_refresh_token")
    if not token:
        raise TokenNoFound
    return token


async def check_refresh_token(token: str = Depends(get_refresh_token),
                              session: AsyncSession = Depends(get_session_without_commit)) -> User:
    """Проверяем refresh_token и возвращаем пользователя."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id = payload.get("sub")

        if not user_id:
            raise NoJwtException

        user = await UsersDAO(session).find_one_or_none_by_id(data_id=int(user_id))

        if not user:
            raise NoJwtException

    except JWTError as e:
        raise NoJwtException from e

    else:
        return user


async def get_current_user(token: str = Depends(get_access_token),
                           session: AsyncSession = Depends(get_session_without_commit)) -> User:
    """Проверяем access_token и возвращаем пользователя."""
    try:
        # Декодируем токен
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError as e:
        raise TokenExpiredException from e
    except JWTError as exc:
        # Общая ошибка для токенов
        raise NoJwtException from exc

    expire: str = payload.get("exp")
    expire_time = datetime.fromtimestamp(int(expire), tz=UTC)
    if (not expire) or (expire_time < datetime.now(UTC)):
        raise TokenExpiredException

    user_id: str = payload.get("sub")
    if not user_id:
        raise NoUserIdException

    user = await UsersDAO(session).find_one_or_none_by_id(data_id=int(user_id))
    if not user:
        raise UserNotFoundException
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Проверяем права пользователя как администратора."""
    if current_user.role == UserRole.ADMIN:
        return current_user
    raise ForbiddenException


async def get_current_techman_user(current_user: User = Depends(get_current_user)) -> User:
    """Проверяем права пользователя как технолога."""
    if current_user.role == UserRole.TECHMAN:
        return current_user
    raise ForbiddenException
