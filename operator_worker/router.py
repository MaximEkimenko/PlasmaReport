"""Routers сервиса operator."""

from fastapi import APIRouter

from exceptions import ServerNotImplementedError

router = APIRouter()


@router.get("/placeholder", tags=["operator"])
async def placeholder() -> None:
    """Данный функционал не планируется реализовывать в MVP."""
    return ServerNotImplementedError
