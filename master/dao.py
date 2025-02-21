"""DAO сервиса master."""

from db.base_dao import BaseDAO
from techman.models import FioDoer


class FioDoerDAO(BaseDAO[FioDoer]):
    """Placeholder."""

    model = FioDoer
