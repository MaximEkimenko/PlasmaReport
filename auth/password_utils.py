"""Настройки проверки паролей приложения auth."""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Получение hash пароля."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Верификация hash пароля."""
    return pwd_context.verify(plain_password, hashed_password)
