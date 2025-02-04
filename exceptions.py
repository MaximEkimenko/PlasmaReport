"""Исключения приложения."""
from fastapi import HTTPException, status

# Пользователь уже существует
UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Пользователь уже существует",
)

# Пользователь не найден
UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователь не найден",
)

# Отсутствует идентификатор пользователя
UserIdNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Отсутствует идентификатор пользователя",
)

# Неверная почта или пароль
IncorrectEmailOrPasswordException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Неверная почта или пароль",
)

# Токен истек
TokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен истек",
)

# Некорректный формат токена
InvalidTokenFormatException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Некорректный формат токена",
)

# Токен отсутствует в заголовке
TokenNoFound = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Токен отсутствует в заголовке",
)

# Невалидный JWT токен
NoJwtException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен не валидный",
)

# Не найден ID пользователя
NoUserIdException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Не найден ID пользователя",
)

# Недостаточно прав
ForbiddenException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Недостаточно прав",
)

TokenInvalidFormatException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Неверный формат токена. Ожидается 'Bearer <токен>'",
)


class WrongTranslateSettingsError(Exception):
    """Исключение для валидации словаря перевода колонок БД."""

    def __init__(self, *,
                 column_names: tuple | None = None,
                 translate_dict: dict | None = None,
                 error_args: str | None = None,
                 ) -> None:
        """Инициализация текста исключения."""
        if column_names and translate_dict:
            msg = (f"Несовпадения словаря настроек с БД - длина БД:{len(column_names)}, "
                   f"длина настроек {len(translate_dict)}.")
        elif error_args:
            msg = f"В словаре настроек translate_dict неверно заполнено: {error_args}."
        else:
            msg = f"Ошибка {error_args}."
        super().__init__(msg)
