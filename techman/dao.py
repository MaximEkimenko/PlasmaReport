"""DAO сервиса techman."""

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from db.base_dao import BaseDAO
from logger_config import log
from techman.enums import ProgramStatus
from techman.models import WO, Part, FioDoer, Program, ProgramFioDoerAssociation


class ProgramDAO(BaseDAO[Program]):
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


    async def update_doer_fios(self, id_fio_doers: list[dict]) -> int:
        """Обновление сполнителей сотрудников программы."""
        try:
            # async with session.begin():
            # Step 1: Получаем все существующие Program IDs
            program_ids = [item["id"] for item in id_fio_doers]
            # programs_query = select(Program.id).where(Program.id.in_(program_ids))
            # result = await self._session.execute(programs_query)
            # existing_program_ids = {row.id for row in result}
            #
            # if not existing_program_ids:
            #     msg = "No valid Program IDs provided."
            #     raise ValueError(msg)

            # Проверяем, что все указанные Program IDs существуют
            # invalid_program_ids = set(program_ids) - existing_program_ids
            # if invalid_program_ids:
            #     msg = f"Programs with IDs {invalid_program_ids} do not exist."
            #     raise ValueError(msg)

            # Step 2: Получаем все FioDoer IDs
            fio_doers_ids = {fio_id for item in id_fio_doers for fio_id in item["fio_doers_ids"]}
            fio_doers_query = select(FioDoer.id).where(FioDoer.id.in_(fio_doers_ids))
            result = await self._session.execute(fio_doers_query)
            existing_fio_doers_ids = {row.id for row in result}

            if not existing_fio_doers_ids:
                msg = "No valid FioDoer IDs provided."
                raise ValueError(msg)

            # Проверяем, что все указанные FioDoer IDs существуют
            invalid_fio_doers_ids = fio_doers_ids - existing_fio_doers_ids
            if invalid_fio_doers_ids:
                msg = f"FioDoers with IDs {invalid_fio_doers_ids} do not exist."
                raise ValueError(msg)

            # Step 3: Очищаем старые связи в промежуточной таблице
            await self._session.execute(
                delete(ProgramFioDoerAssociation).where(ProgramFioDoerAssociation.program_id.in_(program_ids)),
            )

            # Step 4: Готовим новые записи для промежуточной таблицы
            new_associations = [
                {"program_id": item["id"], "fio_doer_id": fio_id}
                for item in id_fio_doers
                for fio_id in item["fio_doers_ids"]
            ]

            # Step 5: Добавляем новые связи
            if new_associations:
                await self._session.execute(
                    insert(ProgramFioDoerAssociation),
                    new_associations,
                )

            await self._session.commit()
            log.success("Успешная запись в БД.")
        except Exception as e:
            await self._session.rollback()
            msg = "Failed to update program fio_doers"
            raise RuntimeError(msg) from e


    # TODO
    async def get_all_with_doers(self, filter_dict: dict | None = None) -> list:
        """Получение всех записей по фильтру схемы pydentic."""
        # filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
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




class WoDAO(BaseDAO[WO]):
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


class PartDAO(BaseDAO[Part]):
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

    async def get_joined_part_data_statuses(self, include_statuses: tuple[str, ...]) -> list[dict]:
        """Получение существующих программ по статусам."""
        query = (
            select(self.model)
            .join(self.model.program)  # Явное присоединение таблицы Program
            .where(self.model.program.has(
                Program.program_status.in_(include_statuses)))  # Проверка program_status через has()
            .options(
                joinedload(self.model.program),  # Предварительная загрузка Program
                joinedload(self.model.wo_number),  # Предварительная загрузка WO
                joinedload(self.model.storage_cell),  # Предварительная загрузка StorageCell
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



