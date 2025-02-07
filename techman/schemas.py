"""Схемы сервиса Techman."""

from pydantic import Field, BaseModel


class SPartData(BaseModel):
    """Все данные программы."""

    name: str = Field(description="Название программы.", example="Techman")




# pr.ProgramName,
#
# pr.RepeatID as RepeatIDProgram,
# p.RepeatID as RepeatIDPart,
#
# pr.UsedArea,
#
# pr.ScrapFraction,
# pr.MachineName,
#
# pr.CuttingTime as CuttingTimeProgram,
# p.CuttingTime as CuttingTimePart,
# p.TotalCuttingTime,
# p.CuttingLength,
#
# pr.PostDateTime,
# pr.Material,
# pr.SheetLength,
# pr.SheetWidth,
# pr.ArchivePacketID,
# pr.TimeLineID,
# pr.Comment,
# pr.PostedByUserID,
# pr.UsedArea,
# pr.UsedArea,
#
# us.UserName,
# us.UserFirstName,
# us.UserLastName,
# us.UserEMail,
# us.LastLoginDate,
#
# w.WONumber,
# w.CustomerName,
# w.WODate,
# w.WOData1,
# w.WOData2,
# w.DateCreated,
#
# p.PartName,
# p.QtyInProcess,
# p.PartLength,
# p.PartWidth,
# p.RectArea,
# p.TrueArea,
# p.TrueWeight,
# p.RectWeight,
#
# p.PierceQty,
# p.MasterPartQty,
# p.WOState,
# p.DueDate,
# p.RevisionNumber,
# p.PK_PIP

class SPartDataList(BaseModel):
    """Список программ."""

    programs: list[SPartData]
