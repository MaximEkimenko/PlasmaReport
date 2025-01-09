from config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, declared_attr, class_mapper
from sqlalchemy import Integer, TIMESTAMP, func
import datetime
from logger_config import log

database_url = settings.db_url
engine = create_async_engine(url=database_url)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP,
                                                 server_default=func.now(), onupdate=func.now())

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def to_dict(self) -> dict:
        columns = class_mapper(self.__class__).columns
        return {column.key: getattr(self, column.key) for column in columns}


def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await method(*args, **kwargs, session=session)
            except Exception as e:
                await session.rollback()
                log.error(f"Ошибка подключения к БД.")
                log.exception(e)
            finally:
                await session.close()
    return wrapper
