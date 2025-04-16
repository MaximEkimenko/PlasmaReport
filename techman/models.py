"""Модели сервиса techman."""
# TODO разнести модели по своим приложениям
import datetime

from decimal import Decimal

from sqlalchemy import TEXT, TIMESTAMP, ForeignKey, UniqueConstraint, text
from sqlalchemy.orm import Mapped, relationship, mapped_column

from auth.models import User
from db.database import Base, uniq_string
from master.enums import Jobs
from techman.enums import WoStatus, PartStatus, ProgramStatus, ProgramPriority


class ProgramFioDoerAssociation(Base):
    """Модель связи программы и исполнителя."""

    program_id: Mapped[int] = mapped_column(ForeignKey("program.id",
                                                       name="fk_association_program_id"), nullable=False)
    fio_doer_id: Mapped[int] = mapped_column(ForeignKey("fiodoer.id",
                                                        name="fk_association_fio_doer_id"), nullable=False)
    __table_args__ = (
        UniqueConstraint("program_id", "fio_doer_id", name="uix_program_fio_doer"),  # Уникальность сочетания
    )


class Program(Base):
    """Модель программ плазменной резки."""

    ProgramName: Mapped[uniq_string] = mapped_column(index=True)  # ProgramName
    RepeatIDProgram: Mapped[str]  # RepeatIDPart
    UsedArea: Mapped[float]  # UsedArea
    ScrapFraction: Mapped[float]  # ScrapFraction
    MachineName: Mapped[str]  # MachineName
    CuttingTimeProgram: Mapped[Decimal]  # CuttingTime
    PostDateTime: Mapped[datetime] = mapped_column(TIMESTAMP)  # PostDateTime
    Material: Mapped[str]  # Material
    Thickness: Mapped[float]  # Thickness
    SheetLength: Mapped[float]  # SheetLength
    SheetWidth: Mapped[float]  # SheetWidth
    ArchivePacketID: Mapped[int]  # ArchivePacketID
    TimeLineID: Mapped[int]  # TimeLineID
    Comment: Mapped[str] = mapped_column(TEXT, default="")  # Comment
    PostedByUserID: Mapped[int]  # PostedByUserID
    PierceQtyProgram: Mapped[int]  # PierceQtyProgram
    # techman user data from user_table
    UserName: Mapped[str] = mapped_column(default="")  # UserName
    UserFirstName: Mapped[str] = mapped_column(default="")  # UserFirstName
    UserLastName: Mapped[str] = mapped_column(default="")  # UserLastName
    UserEMail: Mapped[str] = mapped_column(default="", nullable=True)  # UserEmail
    LastLoginDate: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)  # LastLoginDate

    # путь к файлу раскладку ods
    path_to_ods: Mapped[str] = mapped_column(default="", nullable=True)
    # мастер
    master_fio_id: Mapped[int] = mapped_column(ForeignKey("fiodoer.id",
                                                          name="fk_program_master_fio_id"), nullable=True)
    # время начала работы программы
    time_program_started: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    # время окончания работы программы
    time_program_finished: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)

    # TODO добавить поле для хранения ссылки на полученную из ods картинку программы ?

    parts: Mapped[list["Part"]] = relationship("Part", back_populates="program")
    program_status: Mapped[ProgramStatus] = mapped_column(default=ProgramStatus.CREATED, index=True)
    program_priority: Mapped[ProgramPriority] = mapped_column(default=ProgramPriority.LOW,
                                                              server_default=text("LOW"), index=True)
    # many_to_many к fio_doer_id
    fio_doers: Mapped[list["FioDoer"]] = relationship(
        "FioDoer", secondary="programfiodoerassociation", back_populates="programs",
    )

    def __str__(self) -> str:
        """Строковое представление для админ панели."""
        return self.__class__.__name__ + f"({self.ProgramName})"


class FioDoer(Base):
    """Модель исполнителей."""

    # TODO добавить поле fio_doer составным из user.first_name и user.last_name
    fio_doer: Mapped[uniq_string]
    position: Mapped[Jobs] = mapped_column(default=Jobs.OPERATOR)
    is_active: Mapped[bool] = mapped_column(default=True, server_default=text("true"))

    programs: Mapped[list["Program"]] = relationship(
        "Program", secondary="programfiodoerassociation", back_populates="fio_doers",
    )

    parts: Mapped[list["Part"]] = relationship("Part", back_populates="done_by_fio_doer")

    # Связь one-to-one с User
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", name="fk_fiodoer_user_id"), unique=True, nullable=True,
    )
    user: Mapped[User] = relationship(back_populates="fio_doer")

    def __str__(self) -> str:
        """Строковое представление для админ панели."""
        return self.__class__.__name__ + f"({self.fio_doer})"


class WO(Base):
    """Модель номеров заказов на плазменную резку."""

    WONumber: Mapped[uniq_string] = mapped_column(index=True)  # WONumber
    CustomerName: Mapped[str]  # CustomerName
    WODate: Mapped[datetime] = mapped_column(TIMESTAMP)  # WODate
    OrderDate: Mapped[datetime] = mapped_column(TIMESTAMP)  # OrderDate
    WOData1: Mapped[str] = mapped_column(default="", nullable=True)  # WOData1
    WOData2: Mapped[str] = mapped_column(default="", nullable=True)  # WOData2
    DateCreated: Mapped[datetime] = mapped_column(TIMESTAMP)  # DateCreated

    parts: Mapped[list["Part"]] = relationship("Part", back_populates="wo_number")
    wo_status: Mapped[WoStatus] = mapped_column(default=WoStatus.CREATED, index=True)


class Part(Base):
    """Модель деталей заказа на плазменную резку."""

    wo_number_id: Mapped[int] = mapped_column(ForeignKey("wo.id", name="fk_part_wo_number_id"))
    wo_number: Mapped[WO] = relationship("WO", back_populates="parts")

    program_id: Mapped[int] = mapped_column(ForeignKey("program.id", name="fk_part_program_id"))
    program: Mapped[Program] = relationship("Program", back_populates="parts")

    storage_cell_id: Mapped[int] = mapped_column(ForeignKey("storagecell.id",
                                                            name="fk_part_storage_cell_id"), nullable=True)
    storage_cell: Mapped[Program] = relationship("StorageCell", back_populates="parts")

    # сделано исполнителем
    done_by_fio_doer_id: Mapped[int] = mapped_column(ForeignKey("fiodoer.id",
                                                                name="fk_part_done_by_fio_doer_id"), nullable=True)
    done_by_fio_doer: Mapped["FioDoer"] = relationship("FioDoer", back_populates="parts")

    PartName: Mapped[str] = mapped_column(index=True)  # PartName
    # RepeatIDPart: Mapped[int] = mapped_column(nullable=True)  # RepeatID
    QtyInProcess: Mapped[int]  # QtyInProcess
    PartLength: Mapped[float]  # PartLength
    PartWidth: Mapped[float]  # PartWidth
    TrueArea: Mapped[float]  # TrueArea
    RectArea: Mapped[float]  # RectArea
    TrueWeight: Mapped[float]  # TrueWeight
    RectWeight: Mapped[float]  # RectWeight
    CuttingTimePart: Mapped[Decimal]  # CuttingTime
    CuttingLength: Mapped[float]  # CuttingLength
    PierceQtyPart: Mapped[int]  # PierceQtyPart
    NestedArea: Mapped[float]  # NestedArea
    TotalCuttingTime: Mapped[Decimal]  # TotalCuttingTime
    MasterPartQty: Mapped[int]  # MasterPartQty
    WOState: Mapped[str]  # WOState
    DueDate: Mapped[datetime] = mapped_column(TIMESTAMP)  # DueDate
    RevisionNumber: Mapped[str]  # RevisionNumber
    PK_PIP: Mapped[str]  # PK_PIP
    Thickness: Mapped[float]  # Thickness
    # TODO добавить поле для хранения ссылки на скопированную картинку детали ?

    part_status: Mapped[PartStatus] = mapped_column(default=PartStatus.UNASSIGNED, index=True)
    # фактически изготовленное количество деталей
    qty_fact: Mapped[int] = mapped_column(nullable=True, default=0)
    # путь к dxf файлу детали из SigmaNest
    SourceFileName: Mapped[str] = mapped_column(TEXT, default="", nullable=True)

    # для каждой программы уникальная деталь
    __table_args__ = (
        UniqueConstraint("PartName", "program_id", "wo_number_id", name="uq_part_program_wo"),
    )

    def __str__(self) -> str:
        """Строковое представление для админ панели."""
        return self.__class__.__name__ + f"({self.PartName})"


class StorageCell(Base):
    """Модель мест хранения деталей."""

    cell_name: Mapped[uniq_string] = mapped_column(index=True)
    parts: Mapped[list["Part"]] = relationship("Part", back_populates="storage_cell")
