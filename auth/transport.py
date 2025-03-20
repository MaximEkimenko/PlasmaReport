"""Транспорты аутентификации."""
from fastapi_users.authentication import BearerTransport, CookieTransport

bearer_transport = BearerTransport(tokenUrl="auth/login")
cookie_transport = CookieTransport(cookie_max_age=60, cookie_secure=False)
