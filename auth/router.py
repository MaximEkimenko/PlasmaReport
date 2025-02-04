"""Auth endpoints."""

from typing import Annotated

from fastapi import Depends, Response, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dao import UsersDAO
from auth.utils import set_tokens, authenticate_user
from exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException
from auth.models import User
from auth.schemas import SUserAuth, SUserInfo, EmailModel, SUserAddDB, SUserRegister
from auth.router_docs import me_docs, login_docs, logout_docs, refresh_docs, register_docs, all_users_docs
from dependencies.dao_dep import get_session_with_commit, get_session_without_commit
from dependencies.auth_dep import get_current_user, check_refresh_token, get_current_admin_user

router = APIRouter()


@router.post("/register/", **register_docs)
async def register_user(user_data: SUserRegister,
                        session: Annotated[AsyncSession, Depends(get_session_with_commit)]) -> dict:
    """Регистрация пользователя."""
    user_dao = UsersDAO(session)

    existing_user = await user_dao.find_one_or_none(filters=EmailModel(email=user_data.email))

    if existing_user:
        raise UserAlreadyExistsException

    # Подготовка данных для добавления
    user_data_dict = user_data.model_dump()
    user_data_dict.pop("confirm_password", None)

    # Добавление пользователя
    await user_dao.add(values=SUserAddDB(**user_data_dict))

    return {"message": "Вы успешно зарегистрированы!"}


@router.post("/login/", **login_docs)
async def auth_user(response: Response,
                    user_data: SUserAuth,
                    session: Annotated[AsyncSession, Depends(get_session_without_commit)]) -> dict:
    """Аутентификация пользователя.

    - **email**: Действительная электронная почта с разрешённым доменом.
    - **password**: Пароль пользователя, длина которого должна быть от 5 до 20 символов.

    Возвращает:
    - **ok**: Статус операции (`True` при успехе).
    - **message**: Сообщение об успешной аутентификации.
    """
    users_dao = UsersDAO(session)
    user = await users_dao.find_one_or_none(
        filters=EmailModel(email=user_data.email),
    )

    if not (user and await authenticate_user(user=user, password=user_data.password)):
        raise IncorrectEmailOrPasswordException
    # установка jwt токенов доступа
    set_tokens(response, user.id)

    return {
        "ok": True,
        "message": "Авторизация успешна!",
    }


@router.post("/logout", **logout_docs)
async def logout(response: Response) -> dict:
    """Выход пользователя."""
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return {"message": "Пользователь успешно вышел из системы"}


@router.get("/me/", **me_docs)
async def get_me(user_data: Annotated[User, Depends(get_current_user)]) -> SUserInfo:
    """Получение данных о текущем пользователе.

    Возвращает:
    - **id**: Уникальный идентификатор пользователя.
    - **email**: Электронная почта пользователя.
    - **first_name**: Имя пользователя.
    - **last_name**: Фамилия пользователя.
    """
    return SUserInfo.model_validate(user_data)


@router.get("/all_users/", **all_users_docs)
async def get_all_users(session: Annotated[AsyncSession, Depends(get_session_with_commit)],
                        user_data: Annotated[User, Depends(get_current_admin_user)]) -> list[SUserInfo]:  # noqa ARG001
    """Получение списка всех пользователей.

    Возвращает:
    - **List[SUserInfo]**: Список объектов, содержащих информацию о пользователях.
      Каждый объект включает:
        - **id**: Уникальный идентификатор пользователя.
        - **email**: Электронная почта пользователя.
        - **first_name**: Имя пользователя.
        - **last_name**: Фамилия пользователя.
    """
    return await UsersDAO(session).find_all()


@router.post("/refresh", **refresh_docs)
async def process_refresh_token(response: Response,
                                user: Annotated[User, Depends(check_refresh_token)]) -> dict:
    """Обновление access и refresh токенов.

    Возвращает:
    - **message**: Сообщение о результате обновления токенов.
    """
    set_tokens(response, user.id)
    return {"message": "Токены успешно обновлены"}
