"""Базовый класс объекта доступа к базе данных."""
# TODO проверить резонность использования flush
from typing import Generic, TypeVar
from collections.abc import Sequence

from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy import delete as sqlalchemy_delete
from sqlalchemy import update as sqlalchemy_update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import Base
from logger_config import log

# from .database import Base

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    """Базовый класс объекта доступа к данным."""

    model: type[T] = None

    def __init__(self, session: AsyncSession) -> None:
        """Инициализация базового объекта доступа к базе данных."""
        self._session = session
        if self.model is None:
            msg = "Модель должна быть указана в дочернем классе"
            raise ValueError(msg)

    async def find_one_or_none_by_id(self, data_id: int) -> T:
        """Получение одной записи по id."""
        try:
            query = select(self.model).filter_by(id=data_id)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
            log_message = f"Запись {self.model.__name__} с ID {data_id} {'найдена' if record else 'не найдена'}."
            log.info(log_message)
        except SQLAlchemyError as e:
            log.error(f"Ошибка при поиске записи с ID {data_id}: {e}")
            raise
        else:
            return record

    async def find_one_or_none(self, filters: BaseModel) -> T:
        """Получение одной записи по фильтру схемы pydentic."""
        filter_dict = filters.model_dump(exclude_unset=True)
        log.info(f"Поиск одной записи {self.model.__name__} по фильтрам: {filter_dict}")
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
        except SQLAlchemyError as e:
            log.error(f"Ошибка при поиске записи по фильтрам {filter_dict}: {e}")
            raise
        else:
            log_message = f"Запись {'найдена' if record else 'не найдена'} по фильтрам: {filter_dict}"
            log.info(log_message)
            return record

    async def find_all(self, filters: BaseModel | None = None) -> list[T]:
        """Получение всех записей по фильтру схемы pydentic."""
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        log.info(f"Поиск всех записей {self.model.__name__} по фильтрам: {filter_dict}")
        try:
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            records = result.scalars().all()
        except SQLAlchemyError as e:
            log.error(f"Ошибка при поиске всех записей по фильтрам {filter_dict}: {e}")
            raise
        else:
            log.info(f"Найдено {len(records)} записей.")
            return list(records)

    async def add(self, values: BaseModel) -> T:
        """Добавление записи в базу данных."""
        values_dict = values.model_dump(exclude_unset=True)
        log.info(f"Добавление записи {self.model.__name__} с параметрами: {values_dict}")
        try:
            new_instance = self.model(**values_dict)
            self._session.add(new_instance)
        except SQLAlchemyError as e:
            log.error(f"Ошибка при добавлении записи: {e}")
            raise
        else:
            log.info(f"Запись {self.model.__name__} успешно добавлена.")
            await self._session.flush()
            return new_instance

    async def add_many(self, instances: list[BaseModel]) -> Sequence[T]:
        """Добавление нескольких записей в базу данных."""
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        log.info(f"Добавление нескольких записей {self.model.__name__}. Количество: {len(values_list)}")
        try:
            new_instances = [self.model(**values) for values in values_list]
            self._session.add_all(new_instances)
        except SQLAlchemyError as e:
            log.error(f"Ошибка при добавлении нескольких записей: {e}")
            raise
        else:
            log.info(f"Успешно добавлено {len(new_instances)} записей.")
            await self._session.flush()
            return new_instances

    async def update(self, filters: BaseModel, values: BaseModel) -> int:
        """Обновление записей по фильтру."""
        filter_dict = filters.model_dump(exclude_unset=True)
        values_dict = values.model_dump(exclude_unset=True)
        log.info(
            f"Обновление записей {self.model.__name__} по фильтру: {filter_dict} с параметрами: {values_dict}")
        try:
            query = (
                sqlalchemy_update(self.model)
                .where(*[getattr(self.model, k) == v for k, v in filter_dict.items()])
                .values(**values_dict)
                .execution_options(synchronize_session="fetch")
            )
            result = await self._session.execute(query)
        except SQLAlchemyError as e:
            log.error(f"Ошибка при обновлении записей: {e}")
            raise
        else:
            log.info(f"Обновлено {result.rowcount} записей.")
            await self._session.flush()
            return int(result.rowcount)

    async def delete(self, filters: BaseModel) -> int:
        """Удаление записей по фильтру."""
        filter_dict = filters.model_dump(exclude_unset=True)
        log.info(f"Удаление записей {self.model.__name__} по фильтру: {filter_dict}")
        if not filter_dict:
            log.error("Нужен хотя бы один фильтр для удаления.")
            msg = "Нужен хотя бы один фильтр для удаления."
            raise ValueError(msg)
        try:
            query = sqlalchemy_delete(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
        except SQLAlchemyError as e:
            log.error(f"Ошибка при удалении записей: {e}")
            raise
        else:
            log.info(f"Удалено {result.rowcount} записей.")
            await self._session.flush()
            return int(result.rowcount)

    async def count(self, filters: BaseModel | None = None) -> int:
        """Количество записей по фильтру."""
        filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
        log.info(f"Подсчет количества записей {self.model.__name__} по фильтру: {filter_dict}")
        try:
            query = select(func.count(self.model.id)).filter_by(**filter_dict)
            result = await self._session.execute(query)
            count = result.scalar()
        except SQLAlchemyError as e:
            log.error(f"Ошибка при подсчете записей: {e}")
            raise
        else:
            log.info(f"Найдено {count} записей.")
            return count

    async def bulk_update(self, records: list[BaseModel]) -> int:
        """Групповое обновление записей."""
        log.info(f"Массовое обновление записей {self.model.__name__}")
        try:
            updated_count = 0
            for record in records:
                record_dict = record.model_dump()
                if "id" not in record_dict:
                    continue

                update_data = {k: v for k, v in record_dict.items() if k != "id"}
                stmt = (
                    sqlalchemy_update(self.model)
                    .filter_by(id=record_dict["id"])
                    .values(**update_data)
                )

                result = await self._session.execute(stmt)
                updated_count += result.rowcount
        except SQLAlchemyError as e:
            log.error(f"Ошибка при массовом обновлении: {e}")
            raise
        else:
            log.info(f"Обновлено {updated_count} записей")
            await self._session.flush()
            return updated_count

    async def bulk_update_by_field_name(self, records: list[dict], update_field_name: str) -> int:
        """Групповое обновление записей по имени поля."""
        log.info(f"Массовое обновление записей {self.model.__name__}")
        try:
            updated_count = 0
            for record_dict in records:
                if update_field_name not in record_dict:
                    continue

                update_data = {field_name: field_value for field_name, field_value in record_dict.items()}  # noqa
                stmt = (
                    sqlalchemy_update(self.model)
                    .filter_by(**{update_field_name: record_dict[update_field_name]})
                    .values(**update_data)
                )
                result = await self._session.execute(stmt)
                updated_count += result.rowcount
        except SQLAlchemyError as e:
            log.error(f"Ошибка при массовом обновлении: {e}")
            raise
        else:
            log.info(f"Обновлено {updated_count} записей")
            await self._session.flush()
            return updated_count


