"""Утилиты сервиса auth."""
from datetime import UTC, datetime, timedelta

from jose import jwt
from fastapi.responses import Response

from config import settings
from auth.schemas import SUserAuth
from auth.password_utils import verify_password


def create_tokens(data: dict) -> dict:
    """Создание токена."""
    now = datetime.now(UTC)  # Текущее время в UTC

    # AccessToken - 30 минут # TODO исправить после тестов!
    access_expire = now + timedelta(days=30)
    access_payload = data.copy()
    access_payload.update({"exp": int(access_expire.timestamp()), "type": "access"})
    access_token = jwt.encode(
        access_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    # RefreshToken - 7 дней # TODO исправить после тестов!
    refresh_expire = now + timedelta(days=30)
    refresh_payload = data.copy()
    refresh_payload.update({"exp": int(refresh_expire.timestamp()), "type": "refresh"})
    refresh_token = jwt.encode(
        refresh_payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return {"access_token": access_token, "refresh_token": refresh_token}


async def authenticate_user(user: SUserAuth, password: str) -> SUserAuth | None:
    """Авторизация пользователя."""
    if not user or verify_password(plain_password=password, hashed_password=user.password) is False:
        return None
    return user


def set_tokens(response: Response, user_id: int) -> None:
    """Установка токена."""
    new_tokens = create_tokens(data={"sub": str(user_id)})
    access_token = new_tokens.get("access_token")
    refresh_token = new_tokens.get("refresh_token")

    response.set_cookie(
        key="user_access_token",
        value=access_token,
        httponly=True,
        # TODO SET TO TRUE AFTER PUBLISH ON HTTPS
        secure=False,
        samesite="lax",
        # samesite="none",
        expires=datetime.now(UTC) + timedelta(days=30),

    )

    response.set_cookie(
        key="user_refresh_token",
        value=refresh_token,
        httponly=True,
        # TODO SET TO TRUE AFTER PUBLISH ON HTTPS
        secure=False,
        samesite="lax",
        # samesite="none",
        expires=datetime.now(UTC) + timedelta(days=30),
    )


