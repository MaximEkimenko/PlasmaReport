"""DAO сервиса techman."""
from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError

from db.base_dao import BaseDAO
from logger_config import log
from techman.models import WO, Part, Program


class ProgramDAO(BaseDAO):
    """Класс объекта доступа к БД для программы (СЗ)."""

    model = Program

    async def insert_returning(self, values: list) -> dict:
        """Вставка данных с возвратом id новой записи и имени программы."""
        result_programs = await self._session.execute(
            insert(self.model).returning(self.model.id, self.model.ProgramName),
            values,
        )
        return {row.ProgramName: row.id for row in result_programs}

    async def find_one_or_none_by_dict(self, filters: dict) -> dict:
        """Получение одной записи по фильтру схемы pydentic."""
        log.info(f"Поиск одной записи {self.model.__name__} по фильтрам: {filters}")
        try:
            query = select(self.model).filter_by(**filters)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
        except SQLAlchemyError as e:
            log.error(f"Ошибка при поиске записи по фильтрам {filters}: {e}")
            raise
        else:
            log_message = f"Запись {'найдена' if record else 'не найдена'} по фильтрам: {filters}"
            log.info(log_message)
            return record

    async def get_programs_by_names(self, names: list[str]) -> list[dict]:
        """Получение существующих программ."""
        # TODO валидировать входящий список имён
        query = select(Program).where(Program.ProgramName.in_(names))

        # Выполнение запроса
        result = await self._session.execute(query)

        # Получение всех записей
        programs = result.scalars().all()
        return [program.to_dict() for program in programs]


class WoDAO(BaseDAO):
    """Класс объекта доступа к БД для заказа (СЗ)."""

    model = WO

    async def insert_returning(self, values: list) -> dict:
        """Вставка значений с возвращением id номер заказа в словаре."""
        result_wos = await self._session.execute(
            insert(self.model).returning(self.model.id, self.model.WONumber),
            values,
        )
        return {row.WONumber: row.id for row in result_wos}


    async def find_one_or_none_by_dict(self, filters: dict) -> dict:
        """Получение одной записи по фильтру схемы pydentic."""
        log.info(f"Поиск одной записи {self.model.__name__} по фильтрам: {filters}")
        try:
            query = select(self.model).filter_by(**filters)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()
        except SQLAlchemyError as e:
            log.error(f"Ошибка при поиске записи по фильтрам {filters}: {e}")
            raise
        else:
            log_message = f"Запись {'найдена' if record else 'не найдена'} по фильтрам: {filters}"
            log.info(log_message)
            return record

    async def get_wos_by_names(self, names: list[str]) -> list[dict]:
        """Получение существующих программ."""
        # TODO валидировать входящий список имён
        query = select(Program).where(Program.ProgramName.in_(names))

        # Выполнение запроса
        result = await self._session.execute(query)

        # Получение всех записей
        programs = result.scalars().all()
        return [program.to_dict() for program in programs]


class PartDAO(BaseDAO):
    """Класс объекта доступа к БД для детали (СЗ)."""

    model = Part



