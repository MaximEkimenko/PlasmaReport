"""DAO сервиса logist."""
from db.base_dao import BaseDAO
from techman.models import StorageCell


class StorageCellDAO(BaseDAO):
    """DAO сервиса logist."""

    model = StorageCell
