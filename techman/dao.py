# ruff: noqa
"""DAO сервиса techman."""

from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload, selectinload

from exceptions import WrongInputError
from db.base_dao import BaseDAO
from logger_config import log
from techman.enums import ProgramStatus
from master.schemas import SProgramIDWithFios
from techman.models import WO, Part, FioDoer, Program, ProgramFioDoerAssociation
from utils.pics_utils.copy_pics_and_get_links import get_part_image, get_program_image


class ProgramDAO(BaseDAO[Program]):
    """Класс объекта доступа к БД для программы (СЗ)."""

    model = Program

    async def find_programs_by_statuses(self, names: list[ProgramStatus]) -> list[dict]:
        """Получение существующих программ по имени программы."""
        # TODO валидировать входящий список имён
        query = (
            select(self.model)
            .options(
                joinedload(Program.parts)
                .joinedload(Part.wo_number)
            )
            .where(self.model.program_status.in_(names))
        )

        # Выполнение запроса
        result = await self._session.execute(query)

        # Получение всех записей
        programs = result.scalars().unique().all()

        return [
            program.to_dict()
            | {"wo_numbers": list({part.wo_number.WONumber for part in program.parts if part.wo_number})}
            | {"wo_data1": list({part.wo_number.WOData1 for part in program.parts if part.wo_number})}
            | {"program_pic": await get_program_image(program.ProgramName)}
            for program in programs]

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
        # query = select(self.model).options(selectinload(Program.fio_doers)).where(self.model.ProgramName.in_(names))
        query = (
            select(self.model)
            .options(
                selectinload(self.model.parts).selectinload(Part.wo_number)
            )
            .options(selectinload(self.model.fio_doers))  # Загружаем исполнителей
            .where(self.model.ProgramName.in_(names))
        )

        # Выполнение запроса
        result = await self._session.execute(query)

        # Получение всех записей
        programs = result.scalars().all()

        return [program.to_dict()
                | {"WONumber": list({part.wo_number.WONumber for part in program.parts if part.wo_number})}
                | {"fio_doers": [doer.to_dict() for doer in program.fio_doers]}
                for program in programs]

    async def find_programs_by_ids(self, ids: list[int]) -> list[dict]:
        """Получение существующих программ по id."""
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
                update_data = dict(record_dict)
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

    async def update_fio_doers(self, id_fio_doers: list[SProgramIDWithFios]) -> None:
        """Обновление исполнителей сотрудников программы."""
        try:

            # существующие исполнители
            fio_doers_ids = {fio_id for item in id_fio_doers for fio_id in item.fio_doers_ids}
            fio_doers_query = select(FioDoer.id).where(FioDoer.id.in_(fio_doers_ids))
            result = await self._session.execute(fio_doers_query)
            existing_fio_doers_ids = {row.id for row in result}

            if not existing_fio_doers_ids:
                detail = "Пользователей не найдено."
                # TODO вернуть словарь с ключами status: error и msg: по которому выше raise WrongInputError(msg)
                raise WrongInputError(...)

            # Проверяем, что все указанные FioDoer IDs существуют
            invalid_fio_doers_ids = fio_doers_ids - existing_fio_doers_ids
            if invalid_fio_doers_ids:
                detail = f"Пользователь с id {invalid_fio_doers_ids} не существует."
                # TODO вернуть словарь с ключами status: error и msg: по которому выше raise WrongInputError(msg)
                raise WrongInputError(...)

            program_ids = [item.id for item in id_fio_doers]
            await self._session.execute(
                delete(ProgramFioDoerAssociation).where(ProgramFioDoerAssociation.program_id.in_(program_ids)),
            )
            new_associations = [
                {"program_id": item.id, "fio_doer_id": fio_id}
                for item in id_fio_doers
                for fio_id in item.fio_doers_ids
            ]
            # обновление приоритетов программ
            for line in id_fio_doers:
                id_fio_doers_dict = line.model_dump()
                update_data = {
                    field: value for field, value in id_fio_doers_dict.items()
                    if field not in ("id", "fio_doers_ids")
                }
                stmt = (
                    update(self.model)
                    .filter_by(id=line.id)
                    .values(**update_data)
                )
                await self._session.execute(stmt)
                log.success("Программа {line} обновлена: {update_data}", line=line.id, update_data=update_data)
            if new_associations:
                await self._session.execute(
                    insert(ProgramFioDoerAssociation),
                    new_associations,
                )
            log.success("Исполнители программ {doers} обновлены.", doers=existing_fio_doers_ids)
            await self._session.commit()
            log.success("Успешная запись в БД.")
            # TODO вернуть словарь с ключём status: success, msg с успехом
        except WrongInputError as e:
            raise WrongInputError(detail=detail) from e
        except Exception as e:
            # TODO вернуть словарь с ключами status: error и msg: по которому выше raise HttpException(msg)
            await self._session.rollback()
            msg = "Failed to update program fio_doers"
            raise RuntimeError(msg) from e

    async def get_all_with_doers(self, status_list: list | None = None) -> list:
        """Получение всех записей с fio_doer по фильтру схемы pydentic."""
        try:
            query = (
                select(self.model)
                .options(selectinload(Program.fio_doers))
                .options(
                    joinedload(Program.parts)
                    .joinedload(Part.wo_number)
                )
                .where(self.model.program_status.in_(status_list))
            )
            result = await self._session.execute(query)
            records = result.scalars().unique().all()
        except SQLAlchemyError:
            log.error("Ошибка при поиске всех записей по статусам")
            raise
        else:
            log.info("Найдено {len_records} записей.", len_records=len(records))

            return [
                program.to_dict()
                | {"fio_doers": [doer.to_dict() for doer in program.fio_doers]}
                | {"wo_numbers": list({part.wo_number.WONumber for part in program.parts if part.wo_number})}
                | {"wo_data1": list({part.wo_number.WOData1 for part in program.parts if part.wo_number})}
                | {"program_pic": await get_program_image(program.ProgramName)}
                for program in records
            ]

    async def get_program_by_fio_id_with_status(self, fio_doer_id: int, statuses: tuple[ProgramStatus, ...]) -> list:
        """Получение программ по фио исполнителя."""
        query = (
            select(self.model)
            .where(self.model.program_status.in_(statuses))
            .join(self.model.fio_doers)
            .where(FioDoer.id == fio_doer_id)
            .options(joinedload(Program.fio_doers))
        )

        result = await self._session.execute(query)

        programs = result.unique().scalars().all()
        log.info(f"Найдено {len(programs)} программ исполнителя с id {fio_doer_id}.")
        return [
            program.to_dict()
            | {"fio_doer": [fio_doer.to_dict() for fio_doer in program.fio_doers if fio_doer.id == fio_doer_id][0]}
            | {"program_pic": await get_program_image(program.ProgramName)}
            for program in programs
        ]

    async def update_program_status(self, program_id: int, new_status: ProgramStatus) -> None:
        """Обновление статуса программы."""
        log.info(f"Обновление статуса программы {program_id} на {new_status}")
        try:
            query = (
                update(self.model)
                .where(self.model.id == program_id)
                .values(program_status=new_status)
            )
            await self._session.execute(query)
        except SQLAlchemyError as e:
            log.error("Ошибка при обновлении статуса программы.")
            log.exception(e)
            raise
        else:
            log.success("Статус программы {program_id} обновлен на {new_status}.", new_status=new_status,
                        program_id=program_id)


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
        """Получение деталей со всеми связанными данными по списку id программ."""
        query = (
            select(self.model)
            .where(self.model.program_id.in_(ids))
            .options(
                joinedload(self.model.program)  # программы
                .options(
                    selectinload(Program.fio_doers),  # исполнители программы
                ),
                joinedload(self.model.wo_number),  # номера заказов
                joinedload(self.model.storage_cell),  # место хранения
            )
        )
        result = await self._session.execute(query)

        # Получение всех записей
        parts = result.scalars().all()
        output = []

        for part in parts:
            combined_data = (
                    {
                        # **(part.program.to_dict() if part.program else {}),  # данные программы
                        **(part.wo_number.to_dict() if part.wo_number else {}),  # данные заказа
                        **(part.storage_cell.to_dict() if part.storage_cell else {}),  # ячейки хранения
                        "fio_doers": [doer.to_dict() for doer in part.program.fio_doers],  # данные исполнителей
                        **part.to_dict(),  # Данные детали
                    }
                    | {"program_pic": await get_program_image(part.program.ProgramName)}
                    | {"part_pic": await get_part_image(part.PartName)}
            )

            output.append(combined_data)

        return output

    async def get_joined_part_data_statuses(self, include_statuses: tuple[str, ...]) -> list[dict]:
        """Получение существующих программ по статусам."""
        query = (
            select(self.model)
            .where(
                self.model.program.has(Program.program_status.in_(include_statuses)),
            )
            .options(
                joinedload(self.model.program).options(
                    selectinload(Program.fio_doers),
                ),
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
            combined_data = {
                **(part.program.to_dict() if part.program else {}),  # Данные программы
                **(part.wo_number.to_dict() if part.wo_number else {}),  # Данные заказа
                **(part.storage_cell.to_dict() if part.storage_cell else {}),  # ячейки хранения
                "fio_doers": [doer.to_dict() for doer in part.program.fio_doers],  # данные исполнителей
                **part.to_dict(),  # Данные детали
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

    async def tst_get_all_data_from_parts(self) -> list[dict]:
        """Получение всех записей из деталей."""
        query = (
            select(Program)
            .options(
                joinedload(Program.parts)
                .joinedload(Part.wo_number)
            )
        )
        # Выполнение запроса
        result = await self._session.execute(query)
        programs = result.scalars().unique().all()

        # Преобразование данных в требуемый формат
        output = [
            {
                "ProgramName": program.ProgramName,
                "UsedArea": program.UsedArea,
                "ScrapFraction": program.ScrapFraction,
                "MachineName": program.MachineName,
                "PostDateTime": program.PostDateTime,
                "Material": program.Material,
                "Thickness": program.Thickness,
                "SheetLength": program.SheetLength,
                "SheetWidth": program.SheetWidth,
                "CuttingTimeProgram": program.CuttingTimeProgram,
                "PierceQtyProgram": program.PierceQtyProgram,
                "wo_numbers": list({part.wo_number.WONumber for part in program.parts if part.wo_number}),
                "wo_data1": list({part.wo_number.WOData1 for part in program.parts if part.wo_number}),
                "parts": [part.PartName for part in program.parts],
            }
            for program in programs
        ]

        # Вывод результата

        return (output)
