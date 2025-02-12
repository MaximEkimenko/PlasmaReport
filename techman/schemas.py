"""Схемы сервиса Techman."""

import datetime

from decimal import Decimal

from pydantic import Field, BaseModel


class CommonPartData(BaseModel):
    """Общая схема для моделей данных детали sigma nest и PlasmaReport."""

    CuttingLength: float = Field(description="Длина вырезки", example=12.22)
    CuttingTimePart: Decimal = Field(description="Время вырезки", example=Decimal("10.2"))
    DueDate: datetime.datetime = Field(description="Дата готовности.",
                                       example=datetime.datetime.now(datetime.UTC))
    MasterPartQty: int = Field(description="Не определено", example=10)
    PK_PIP: str = Field(description="Не определено", example="FBEC3DC9-4111-41C6-BFA0-62E03451D9E3")
    PartLength: float = Field(description="Длина части", example=10.2)
    PartName: str = Field(description="Название части", example="Part1")
    PartWidth: float = Field(description="Ширина части", example=10.2)
    PierceQtyPart: int = Field(description="Количество врезок", example=10)
    WOState: int = Field(description="Не определено", example="1")
    QtyInProcess: int = Field(description="Количество деталей в процессе", example=10)
    RectArea: float = Field(description="Площадь rect поверхности", example=10.2)
    RectWeight: float = Field(description="Вес rect поверхности", example=10.2)
    RevisionNumber: str = Field(description="Номер ревизии", example="1")
    TotalCuttingTime: Decimal = Field(description="Общее время", example=Decimal("10.2"))
    TrueArea: float = Field(description="Площадь True поверхности", example=10.2)
    TrueWeight: float = Field(description="Вес True поверхности", example=10.2)
    Thickness: float = Field(description="Толщина", example=10.2)
    NestedArea: float = Field(description="Площадь Nested поверхности", example=10.2)


class SPartDataSigma(CommonPartData):
    """Модель данных детали после разделения общего словаря из sigma nest."""

    # Поля для FK при записи
    ProgramName: str = Field(description="Название программы", example="Program1")
    WONumber: str = Field(description="Номер заказа", example="Z325")


class SPartDataPlasmaReport(CommonPartData):
    """Модель данных детали после разделения общего словаря из sigma nest."""

    # Поля для FK при записи
    wo_number_id: int = Field(description="FK названия программы из таблицы WO", example=1)
    program_id: int = Field(description="FK названия программы из таблицы Program", example=2)


class SProgramData(BaseModel):
    """Модель данных программы после разделения общего словаря из sigma nest."""

    ArchivePacketID: int = Field(description="Не определено", example=1)
    Comment: str = Field(description="Комментарий", example="Это какой-то комментарий")
    CuttingTimeProgram: Decimal = Field(description="Время вырезки программы", example=Decimal("10.2"))
    LastLoginDate: datetime.datetime = Field(description="Дата последнего входа технолога",
                                             example=datetime.datetime.now(datetime.UTC))
    MachineName: str = Field(description="Имя плазменной установки", example="Voortman_V304_KJB300SF_L2R")
    Material: str = Field(description="Материал", example="GS")
    PostDateTime: datetime.datetime = Field(description="Дата поста программы",
                                            example=datetime.datetime.now(datetime.UTC))
    PostedByUserID: int = Field(description="ID технолога, который постил программу", example=1)
    ProgramName: str = Field(description="Название программы", example="Program1")
    RepeatIDProgram: int = Field(description="Количество повторов программы", example=1)
    SheetLength: float = Field(description="Длина листа", example=10.2)
    SheetWidth: float = Field(description="Ширина листа", example=10.2)
    ScrapFraction: float = Field(description="Не определено", example=10.2)
    TimeLineID: int = Field(description="Не определено", example=1)
    UsedArea: float = Field(description="Используемая площадь", example=10.2)
    UserEMail: str = Field(description="Email технолога", example="user@example.com")
    UserFirstName: str = Field(description="login технолога", example="user-158")
    UserLastName: str = Field(description="Фамилия технолога", example="User")
    UserName: str = Field(description="Полное имя технолога", example="user-158 User")
    Thickness: float = Field(description="Толщина", example=10.2)
    PierceQtyProgram: int = Field(description="Количество врезок", example=10)


class SWoData(BaseModel):
    """Модель данных заказа после разделения общего словаря из sigma nest."""

    CustomerName: str = Field(description="Название заказчика", example="Customer1")
    DateCreated: datetime.datetime = Field(description="Дата создания заказа",
                                           example=datetime.datetime.now(datetime.UTC))
    OrderDate: datetime.datetime = Field(description="Дата заказа",
                                         example=datetime.datetime.now(datetime.UTC))
    WOData1: str = Field(description="Комментарий к заказу 1", example="4SV185x12")
    WOData2: str = Field(description="Комментарий к заказу 2", example="Plita 1899")
    WODate: datetime.datetime = Field(description="Дата заказа",
                                      example=datetime.datetime.now(datetime.UTC))
    WONumber: str = Field(description="Номер заказа", example="Z325")



