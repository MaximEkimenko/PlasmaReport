"""Объект доступа к БД сервиса reports."""
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from db.base_dao import BaseDAO
from techman.models import Part, Program


class ReportPartDAO(BaseDAO):
    """Объект доступа к БД сервиса reports ля формирования отчёта по деталям."""

    model = Part

    async def get_full_part_data_start_end(self, start_date: date, end_date: date,
                                           _session: AsyncSession = None) -> list[dict]:
        """Получение существующих программ."""
        query = (
            select(self.model)
            .options(
                joinedload(self.model.program)  # программы
                .options(
                    selectinload(Program.fio_doers),  # исполнители программы
                ),
                joinedload(self.model.wo_number),  # данные wo
                joinedload(self.model.storage_cell),  # данные мест хранения
            )
            .where(
                and_(
                    Part.created_at >= start_date,  # Дата создания больше или равна start_date
                    Part.created_at <= end_date,  # Дата создания меньше или равна end_date
                ),
            )
            .order_by(self.model.created_at)  # Сортировка по created_at
        )

        # Выполнение запроса
        result = await self._session.execute(query)
        parts = result.scalars().all()
        output = []
        for part in parts:
            # Объединяем данные детали, программы и заказа в один словарь
            combined_data = {
                **(part.program.to_dict()),  # Данные программы
                **(part.wo_number.to_dict()),  # Данные заказа
                **(part.storage_cell.to_dict() if part.storage_cell else {}),  # Данные мест хранения
                **part.to_dict(),  # Данные детали
            }

            if part.program:
                combined_data["fio_doers"] = [
                    fio_doer.to_dict()
                    for fio_doer in part.program.fio_doers
                ]
            else:
                combined_data["fio_doers"] = []

            output.append(combined_data)

        return output
