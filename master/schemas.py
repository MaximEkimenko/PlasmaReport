"""Схемы сервиса master."""
from pydantic import BaseModel

from master.enums import Jobs
from techman.enums import ProgramStatus, ProgramPriority


class SProgramsStatus(BaseModel):
    """Схема для получения списка программ по статусу."""

    id: int | None = None
    program_status: ProgramStatus | None = None


class SFioDoer(BaseModel):
    """Схема исполнителя."""

    fio_doer: str | None = None
    position: Jobs | None = Jobs.OPERATOR


class SProgramIDWithFios(BaseModel):
    """Схема id программ с fio исполнителя."""

    id: int
    fio_doers_ids: list
    program_status: str = ProgramStatus.ASSIGNED.name
    program_priority: str | None = ProgramPriority.LOW.name


class SProgramWithFioDoer(BaseModel):
    """Схема программ с fio исполнителя."""



# {
#       "ProgramName": "GS- 10-143791",
#       "RepeatIDProgram": "1",
#       "UsedArea": 223930.32440178562,
#       "ScrapFraction": 0.33573087790867384,
#       "MachineName": "Voortman_V304_KJB300SF_L2R",
#       "CuttingTimeProgram": "774.3373529596",
#       "PostDateTime": "2025-02-17T08:58:00",
#       "Material": "GS",
#       "Thickness": 10,
#       "SheetLength": 3906.595585051549,
#       "SheetWidth": 1500,
#       "ArchivePacketID": 35476,
#       "TimeLineID": 89068,
#       "Comment": "",
#       "PostedByUserID": 10,
#       "PierceQtyProgram": 11,
#       "UserName": "user-158",
#       "UserFirstName": "user-158",
#       "UserLastName": "",
#       "UserEMail": "",
#       "LastLoginDate": "2025-02-16T11:26:02",
#       "path_to_ods": null,
#       "master_fio_id": null,
#       "time_program_started": null,
#       "time_program_finished": null,
#       "program_status": "в работе",
#       "program_priority": 4,
#       "id": 2,
#       "created_at": "2025-02-17T03:40:50",
#       "updated_at": "2025-03-03T08:52:58",
#       "fio_doers": [
#         {
#           "fio_doer": "Мастеровой Мастер Мастерович",
#           "position": "мастер",
#           "is_active": true,
#           "id": 4,
#           "created_at": "2025-02-14T06:14:32",
#           "updated_at": "2025-02-14T06:14:32"
#         },
#         {
#           "fio_doer": "Петров П.П.",
#           "position": "оператор",
#           "is_active": true,
#           "id": 5,
#           "created_at": "2025-02-17T09:23:17",
#           "updated_at": "2025-02-17T09:23:17"
#         },
#         {
#           "fio_doer": "Сидоров С.И.",
#           "position": "оператор",
#           "is_active": true,
#           "id": 6,
#           "created_at": "2025-02-17T09:23:43",
#           "updated_at": "2025-02-17T09:23:43"
#         }
#       ]
#     },
