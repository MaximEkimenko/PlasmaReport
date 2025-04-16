"""Middlewares всего проекта PlasmaReport."""
from collections.abc import Callable, Awaitable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Middleware для добавления Cache-Control в ответы."""

    async def dispatch(self,
                       request: Request,
                       call_next: Callable[[Request], Awaitable[Response]],
                       ) -> Response:
        """Добавляет Cache-Control в ответы."""
        response = await call_next(request)
        if request.url.path.startswith("/static/images"):
            response.headers["Cache-Control"] = "public, max-age=31536000"
            response.headers["Expires"] = "31536000"
        return response
