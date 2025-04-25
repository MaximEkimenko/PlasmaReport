"""Auth endpoints."""
from typing import Annotated

from fastapi import Depends, APIRouter

from auth.users import auth_backend, fastapi_users, current_active_user
from auth.models import User
from auth.schemas import UserRead, UserCreate

router = APIRouter()


@router.get("/authenticated-route")
async def authenticated_route(user: Annotated[User, Depends(current_active_user)]) -> dict:
    """Тесты аутентификации."""
    return {"message": f"Hello {user.email}, your role is {user.role}!"}


# FastAPI Users routers
router.include_router(fastapi_users.get_auth_router(auth_backend))
router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
