"""Содели сервиса techman."""
import datetime

from decimal import Decimal

from sqlalchemy import TEXT, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship, mapped_column

from db.database import Base, uniq_string
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
    UserEmail: Mapped[str] = mapped_column(default="")  # UserEmail
    LastLoginDate: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)  # LastLoginDate

    parts: Mapped[list["Part"]] = relationship("Part", back_populates="program")
    program_status: Mapped[ProgramStatus] = mapped_column(default=ProgramStatus.CREATED, index=True)
    # program_name: Mapped[uniq_string]  # ProgramName
    # repeat_id: Mapped[str]  # RepeatID
    # user_area: Mapped[float]  # UsedArea
    # scrap_fraction: Mapped[float]  # ScrapFraction
    # machine_name: Mapped[str]  # MachineName
    # cutting_time: Mapped[Decimal]  # CuttingTime
    # pierce_qty: Mapped[int]  # PierceQuantity
    # post_date_time: Mapped[datetime] = mapped_column(TIMESTAMP)  # PostDateTime
    # material: Mapped[str]  # Material
    # thickness: Mapped[float]  # Thickness
    # sheet_length: Mapped[float]  # SheetLength
    # sheet_width: Mapped[float]  # SheetWidth
    # archive_packet_id: Mapped[int]  # ArchivePacketID
    # time_line_id: Mapped[int]  # TimeLineID
    # comment: Mapped[str] = mapped_column(TEXT, default="")  # Comment
    # post_by_user_id: Mapped[int]  # PostByUserID
    # # techman user data from user_table
    # user_name: Mapped[str] = mapped_column(default="")  # UserName
    # user_first_name: Mapped[str] = mapped_column(default="")  # UserFirstName
    # user_last_name: Mapped[str] = mapped_column(default="")  # UserLastName
    # user_email: Mapped[str] = mapped_column(default="")  # UserEmail
    # user_last_login_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)  # LastLoginDate
    # parts: Mapped[list["Part"]] = relationship("Part", back_populates="program")
    # program_status: Mapped[ProgramStatus] = mapped_column(default=ProgramStatus.CREATED)


class WO(Base):
    """Модель номеров заказов на плазменную резку."""

    # wo_number: Mapped[uniq_string]  # WONumber
    # customer_name: Mapped[str]  # CustomerName
    # wo_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)  # WODate
    # order_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)  # OrderDate
    # wo_data_1: Mapped[str] = mapped_column(default="", nullable=True)  # WOData1
    # wo_data_2: Mapped[str] = mapped_column(default="", nullable=True)  # WOData2
    # date_created: Mapped[datetime] = mapped_column(TIMESTAMP)  # DateCreated
    #
    # parts: Mapped[list["Part"]] = relationship("Part", back_populates="wo_number")
    # wo_status: Mapped[WoStatus] = mapped_column(default=WoStatus.CREATED)
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
    part_status: Mapped[PartStatus] = mapped_column(default=PartStatus.UNASSIGNED, index=True)
    Thickness: Mapped[float]  # Thickness

    # для каждой программы уникальная деталь
    __table_args__ = (
        UniqueConstraint("PartName", "program_id",  name="uq_part_program"),
    )
