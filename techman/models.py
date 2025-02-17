"""Модели сервиса techman."""
import datetime

from decimal import Decimal

from sqlalchemy import TEXT, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from db.database import Base, uniq_string

# from master.models import FioDoer
from master.enums import Jobs
from techman.enums import WoStatus, PartStatus, ProgramStatus


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

    parts: Mapped[list["Part"]] = relationship("Part", back_populates="program")
    program_status: Mapped[ProgramStatus] = mapped_column(default=ProgramStatus.CREATED, index=True)

    fio_doer_id: Mapped[int] = mapped_column(ForeignKey("fiodoer.id"), nullable=True)
    fio_doer: Mapped["FioDoer"] = relationship("FioDoer", back_populates="program", lazy="joined")


class FioDoer(Base):
    """Модель исполнителей."""

    fio_doer: Mapped[uniq_string]
    position: Mapped[Jobs] = mapped_column(default=Jobs.OPERATOR)
    program: Mapped[list["Program"]] = relationship("Program", back_populates="fio_doer")


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

    wo_number_id: Mapped[int] = mapped_column(ForeignKey("wo.id"))
    wo_number: Mapped[WO] = relationship("WO", back_populates="parts")

    program_id: Mapped[int] = mapped_column(ForeignKey("program.id"))
    program: Mapped[Program] = relationship("Program", back_populates="parts")

    storage_cell_id: Mapped[int] = mapped_column(ForeignKey("storagecell.id"), nullable=True)
    storage_cell: Mapped[Program] = relationship("StorageCell", back_populates="parts")

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

    part_status: Mapped[PartStatus] = mapped_column(default=PartStatus.UNASSIGNED, index=True)
    qty_fact: Mapped[int] = mapped_column(nullable=True, default=0)

    # для каждой программы уникальная деталь
    __table_args__ = (
        UniqueConstraint("PartName", "program_id", "wo_number_id",  name="uq_part_program_wo"),
    )


class StorageCell(Base):
    """Модель мест хранения деталей."""

    cell_name: Mapped[uniq_string] = mapped_column(index=True)
    parts: Mapped[list["Part"]] = relationship("Part", back_populates="storage_cell")

