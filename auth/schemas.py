"""Схемы пользователей."""

from typing import Self

from pydantic import Field, EmailStr, BaseModel, ConfigDict, field_validator, model_validator

from auth.enums import UserRole
from settings.constants import ALLOWED_DOMAINS
from auth.password_utils import get_password_hash


class EmailModel(BaseModel):
    """Базовая схема для аутентификации."""

    email: EmailStr = Field(..., description=f"Электронная почта. К регистрации разрешены только {ALLOWED_DOMAINS}.",
                            examples=[f"user@{ALLOWED_DOMAINS[0]}"])
    model_config = ConfigDict(from_attributes=True)

    @field_validator("email")
    def validate_email_domain(cls, value: str) -> str:
        """Валидация поля email."""
        # Проверяем, что email содержит символ '@'
        if "@" not in value:
            msg = "Некорректный формат email"
            raise ValueError(msg)

        # Извлекаем домен из email
        domain = value.split("@")[-1]

        # Проверяем, что домен находится в списке разрешённых
        if domain not in ALLOWED_DOMAINS:
            msg = f"Домен '{domain}' не разрешён"
            raise ValueError(msg)

        return value


class UserBase(EmailModel):
    """Базовый пользователь."""

    first_name: str = Field(min_length=3, max_length=20, description="Имя, от 3 до 20 символов",
                            examples=["Иван"])
    last_name: str = Field(min_length=3, max_length=20, description="Фамилия, от 3 до 20 символов",
                           examples=["Иванов"])
    role: UserRole | None = Field(default=None, description="Роль пользователя. Не обязательное поле. "
                                                             "По умолчанию присваивается USER.",
                                  examples=["USER"])

    @field_validator("first_name", "last_name")
    def validate_first_name_last_name(cls, value: str) -> str:
        """Валидация first_name last_name."""
        if not value.isalpha():
            msg = "Имя и фамилия пользователя должно состоять только из букв."
            raise ValueError(msg)
        return value


class SUserRegister(UserBase):
    """Схема для регистрации пользователя."""

    password: str = Field(min_length=5, max_length=20, description="Пароль, от 5 до 20 знаков",
                          examples=["StrongPass1!"])
    confirm_password: str = Field(min_length=5, max_length=50, description="Повторите пароль",
                                  examples=["StrongPass1!"])

    @model_validator(mode="after")
    def check_password(self) -> Self:
        """Проверка пароля."""
        if self.password != self.confirm_password:
            msg = "Пароли не совпадают"
            raise ValueError(msg)
        self.password = get_password_hash(self.password)  # хешируем пароль до сохранения в базе данных
        return self


class SUserAddDB(UserBase):
    """Схема для добавления в БД."""

    password: str = Field(min_length=5,
                          description="Пароль в формате HASH-строки",
                          examples=["StrongPass1!"])


class SUserAuth(EmailModel):
    """Схема для аутентификации."""

    password: str = Field(min_length=5,
                          max_length=20,
                          description="Пароль, от 5 до 20 знаков",
                          examples=["StrongPass1!"])


class SUserInfo(UserBase):
    """Информация о пользователях."""

    id: int = Field(description="Идентификатор пользователя", examples=[1])
