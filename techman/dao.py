"""DAO сервиса techman."""

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from db.base_dao import BaseDAO
from logger_config import log
from techman.enums import ProgramStatus
from techman.models import WO, Part, Program


class ProgramDAO(BaseDAO):
    """Класс объекта доступа к БД для программы (СЗ)."""

    model = Program

    async def find_programs_by_statuses(self, names: list[ProgramStatus]) -> list[dict]:
        """Получение существующих программ по имени программы."""
        # TODO валидировать входящий список имён
        query = select(self.model).where(self.model.program_status.in_(names))

        # Выполнение запроса
        result = await self._session.execute(query)

        # Получение всех записей
        programs = result.scalars().all()
        return [program.to_dict() for program in programs]

    async def insert_returning(self, values: list) -> dict:
        """Вставка данных с возвратом id новой записи и имени программы."""
        result_programs = await self._session.execute(
            insert(self.model).returning(self.model.id, self.model.ProgramName),
            values,
        )
        return {row.ProgramName: row.id for row in result_programs}

    async def find_programs_by_names(self, names: list[str]) -> list[dict]:
        """Получение существующих программ по имени программы."""
        # TODO валидировать входящий список имён
        query = select(self.model).where(self.model.ProgramName.in_(names))

        # Выполнение запроса
        result = await self._session.execute(query)

        # Получение всех записей
        programs = result.scalars().all()
        return [program.to_dict() for program in programs]

    async def find_programs_by_ids(self, ids: list[int]) -> list[dict]:
        """Получение существующих программ по имени программы."""
        # TODO валидировать входящий список имён
        query = select(self.model).where(self.model.id.in_(ids))

        # Выполнение запроса
        result = await self._session.execute(query)

        # Получение всех записей
        programs = result.scalars().all()
        return [program.to_dict() for program in programs]

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
                    update(self.model)
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

    async def find_wos_by_names(self, wo_numbers: list[str]) -> list[dict]:
        """Получение существующих заказов по имени заказа."""
        # TODO валидировать входящий список имён
        query = select(self.model).where(self.model.WONumber.in_(wo_numbers))

        # Выполнение запроса
        result = await self._session.execute(query)

        # Получение всех записей
        programs = result.scalars().all()
        return [program.to_dict() for program in programs]


class PartDAO(BaseDAO):
    """Класс объекта доступа к БД для детали (СЗ)."""

    model = Part

    async def get_joined_part_data_by_programs_ids_list(self, ids: list[int]) -> list[dict]:
        """Получение существующих программ."""
        query = (
            select(self.model)
            .where(self.model.program_id.in_(ids))
            .options(
                joinedload(self.model.program),
                joinedload(self.model.wo_number),
                joinedload(self.model.storage_cell),
            )
        )
        # Выполнение запроса
        result = await self._session.execute(query)

        # Получение всех записей
        parts = result.scalars().all()
        output = []
        for part in parts:
            # Объединяем данные детали, программы и заказа в один словарь
            combined_data = {
                **(part.program.to_dict() if part.program else {}),  # Данные программы
                **(part.wo_number.to_dict() if part.wo_number else {}),  # Данные заказа
                **part.to_dict(),  # Данные детали
                # **(part.storage_cell.to_dict() if part.wo_number else {}),
                # **(getattr(part, "wo_number", {}).to_dict() if getattr(part, "wo_number", None) else {})
            }
            output.append(combined_data)

        return output

    async def get_parts_by_program_ids(self, ids: list[int]) -> list[dict]:
        """Получение существующих программ."""
        # TODO валидировать входящий список имён
        query = select(self.model).where(self.model.program_id.in_(ids))
        # Выполнение запроса
        result = await self._session.execute(query)
        # Получение всех записей
        parts = result.scalars().all()
        return [part.to_dict() for part in parts]

    async def delete_by_id(self, element_id: int) -> int:
        """Удаление записей по id."""
        # TODO делать BULK_DELETE
        log.info(f"Удаление записей {self.model.__name__} по id: {element_id}")
        try:
            query = delete(self.model).filter_by(id=element_id)
            result = await self._session.execute(query)
        except SQLAlchemyError as e:
            log.error(f"Ошибка при удалении записей: {e}")
            raise
        else:
            log.info(f"Удалено {result.rowcount} записей.")
            await self._session.flush()
            return int(result.rowcount)
