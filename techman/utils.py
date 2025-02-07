"""Утилиты сервиса Techman."""
import datetime

from operator import itemgetter

from logger_config import log
from sigma_handlers.sigma_db import get_parts_data_by_programs

type SeparatedDataList = dict[str, list[dict[str, str | datetime.datetime]]]


async def create_data_to_db(active_programs: list[str]) -> SeparatedDataList:
    """Создание списков словарей данных готовых к записи в БД PlasmaReport."""
    data_programs_wos_parts_list = await get_parts_data_by_programs(active_programs)

    # Разделение на три словаря programs, wos, parts
    # TODO вынести словари в отдельный config?
    program_dict_keys = ("ProgramName",
                         "RepeatIDProgram",
                         "RepeatIDPart",
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
                      "PierceQty",
                      "MasterPartQty",
                      "WOState",
                      "DueDate",
                      "RevisionNumber",
                      "PK_PIP",
                      )

    programs = []
    wos = []
    parts = []

    # Множества для уникальности
    seen_programs = set()
    seen_wos = set()
    seen_parts = set()

    for line_dict in data_programs_wos_parts_list:
        # Создаем программы
        program_frozenset = frozenset((key, line_dict[key]) for key in program_dict_keys)
        if program_frozenset not in seen_programs:
            seen_programs.add(program_frozenset)
            programs.append(dict(zip(program_dict_keys, itemgetter(*program_dict_keys)(line_dict), strict=False)))

        # Создаем WOs
        wo_frozenset = frozenset((key, line_dict[key]) for key in wo_dict_keys)
        if wo_frozenset not in seen_wos:
            seen_wos.add(wo_frozenset)
            wos.append(dict(zip(wo_dict_keys, itemgetter(*wo_dict_keys)(line_dict), strict=False)))

        # Создаем части
        part_frozenset = frozenset((key, line_dict[key]) for key in part_dict_keys)
        if part_frozenset not in seen_parts:
            seen_parts.add(part_frozenset)
            parts.append(dict(zip(part_dict_keys, itemgetter(*part_dict_keys)(line_dict), strict=False)))

        # Проверка на полноту данных
        if not all(key in line_dict for key in program_dict_keys + wo_dict_keys + part_dict_keys):
            # TODO создать своё исключение обработать выше
            log.error("Ошибка при разделении данных sigma на словари для PlasmaReport.")
            raise ValueError

    return {"programs": programs, "wos": wos, "parts": parts}

if __name__ == "__main__":
    _active_programs = ["SP SS- 1-142211", "SP- 3-142202", "SP RIFL- 4-136491", "S390-20-134553"]
    # pprint(asyncio.run(create_data_to_db(_active_programs)))
