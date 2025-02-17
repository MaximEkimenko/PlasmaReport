"""Объект доступа к БД сервиса reports."""
from datetime import date

from sqlalchemy import and_, select
from sqlalchemy.orm import joinedload

from db.base_dao import BaseDAO
from techman.models import Part, Program


class ReportPartDAO(BaseDAO):
    """Объект доступа к БД сервиса reports ля формирования отчёта по деталям."""

    model = Part

    async def get_full_part_data_start_end(self, start_date: date, end_date: date) -> list[dict]:
        """Получение существующих программ."""
        query = (
            select(self.model)
            .options(
                joinedload(self.model.wo_number),  # данные wo
                joinedload(self.model.program).joinedload(Program.fio_doer),  # данные программ
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

        # Получение всех записей
        parts = result.scalars().all()
        output = []
        for part in parts:
            # Объединяем данные детали, программы и заказа в один словарь
            combined_data = {
                **part.to_dict(),  # Данные детали
                **(part.program.to_dict() if part.program else {}),  # Данные программы
                **(part.wo_number.to_dict() if part.wo_number else {}),  # Данные заказа
                **(part.storage_cell.to_dict() if part.storage_cell else {}),  # Данные мест хранения
                **(part.program.fio_doer.to_dict() if part.program.fio_doer else {}),  # Данные сотрудника
            }
            output.append(combined_data)

        return output


