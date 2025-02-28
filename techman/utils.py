"""Утилиты сервиса Techman."""
import asyncio

from typing import Any
from decimal import Decimal
from operator import itemgetter
from collections import defaultdict

from logger_config import log
from sigma_handlers.sigma_db import get_parts_data_by_programs


async def create_data_to_db(active_programs: list[str]) -> dict[str, list[dict[str, Any]]]:
    """Создание списков словарей данных готовых к записи в БД PlasmaReport."""
    data_programs_wos_parts_list = await get_parts_data_by_programs(active_programs)

    # Разделение на три словаря programs, wos, parts
    # TODO вынести словари в отдельный config?
    program_dict_keys = ("ProgramName",
                         "RepeatIDProgram",
                         "UsedArea",
                         "ScrapFraction",
                         "MachineName",
                         "CuttingTimeProgram",
                         "PostDateTime",
                         "Material",
                         "SheetLength",
                         "SheetWidth",
                         "ArchivePacketID",
                         "TimeLineID",
                         "Comment",
                         "PostedByUserID",
                         "UsedArea",
                         "UsedArea",
                         "UserName",
                         "UserFirstName",
                         "UserLastName",
                         "UserEMail",
                         "LastLoginDate",
                         "Thickness",
                         "PierceQtyProgram",
                         )
    wo_dict_keys = ("WONumber",
                    "WODate",
                    "WOData1",
                    "WOData2",
                    "DateCreated",
                    "CustomerName",
                    "CustomerName",
                    "CustomerName",
                    "CustomerName",
                    "OrderDate",
                    )
    part_dict_keys = ("CuttingTimePart",
                      "TotalCuttingTime",
                      "CuttingLength",
                      "PartName",
                      "WONumber",
                      "ProgramName",
                      "QtyInProcess",
                      "PartLength",
                      "PartWidth",
                      "RectArea",
                      "TrueArea",
                      "TrueWeight",
                      "RectWeight",
                      "MasterPartQty",
                      "WOState",
                      "DueDate",
                      "RevisionNumber",
                      "PK_PIP",
                      "Thickness",
                      "PierceQtyPart",
                      "NestedArea",
                      "SourceFileName",
                      )

    wos = []
    parts = []
    seen_wos = set()
    seen_parts = set()
    max_programs = defaultdict(dict)
    for line_dict in data_programs_wos_parts_list:
        program_name = line_dict.get("ProgramName")
        repeat_id_program = line_dict.get("RepeatIDProgram")
        # определение записи с максимальным RepeatIDProgram
        if not max_programs[program_name] or repeat_id_program > max_programs[program_name]["RepeatIDProgram"]:
            max_programs[program_name] = line_dict
        # WOs
        wo_frozenset = frozenset((key, line_dict[key]) for key in wo_dict_keys)
        if wo_frozenset not in seen_wos:
            seen_wos.add(wo_frozenset)
            wos.append(dict(zip(wo_dict_keys, itemgetter(*wo_dict_keys)(line_dict), strict=False)))

        # Parts
        part_frozenset = frozenset((key, line_dict[key]) for key in part_dict_keys)
        if part_frozenset not in seen_parts:
            seen_parts.add(part_frozenset)
            parts.append(dict(zip(part_dict_keys, itemgetter(*part_dict_keys)(line_dict), strict=False)))

        # Проверка на полноту данных
        if not all(key in line_dict for key in program_dict_keys + wo_dict_keys + part_dict_keys):
            # TODO создать своё исключение обработать выше
            log.error("Ошибка при разделении данных sigma на словари для PlasmaReport.")
            raise ValueError

    programs = [
        dict(zip(program_dict_keys, itemgetter(*program_dict_keys)(line_dict), strict=False))
        for line_dict in max_programs.values()
    ]
    return {"programs": programs, "wos": wos, "parts": parts}


def normalize_value(value: str | float | Decimal) -> int:
    """Функция для нормализации значений float и Decimal для корректного сравнения."""
    return int(value) if isinstance(value, Decimal | float) else value


if __name__ == "__main__":
    # _active_programs = ["SP SS- 1-142211", "SP- 3-142202", "SP RIFL- 4-136491", "S390-20-134553"]
    _active_programs = ["SP RIFL- 4-142696",
                        ]
    data = (asyncio.run(create_data_to_db(_active_programs)))
    # pprint(data["parts"])
    # pprint(data["wos"])
