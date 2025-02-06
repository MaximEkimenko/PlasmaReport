"""Содели сервиса techman."""
import datetime

from decimal import Decimal

from enums import WoStatus, PartStatus, ProgramStatus
from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from db.database import Base


class Program(Base):
    """Модель программ плазменной резки."""

    program_name: Mapped[str]  # ProgramName
    repeat_id: Mapped[str]  # RepeatID
    user_area: Mapped[float]  # UsedArea
    scrap_fraction: Mapped[float]  # ScrapFraction
    machine_name: Mapped[str]  # MachineName
    cutting_time: Mapped[Decimal]  # CuttingTime
    pierce_qty: Mapped[int]  # PierceQuantity
    post_date_time: Mapped[datetime] = mapped_column(TIMESTAMP)  # PostDateTime
    material: Mapped[str]  # Material
    thickness: Mapped[float]  # Thickness
    sheet_length: Mapped[float]  # SheetLength
    sheet_width: Mapped[float]  # SheetWidth
    archive_packet_id: Mapped[int]  # ArchivePacketID
    time_line_id: Mapped[int]  # TimeLineID
    comment: Mapped[str] = mapped_column(default="")  # Comment
    post_by_user_id: Mapped[int]  # PostByUserID
    user_name: Mapped[str] = mapped_column(default="")  # UserName
    user_first_name: Mapped[str] = mapped_column(default="")  # UserFirstName
    user_last_name: Mapped[str] = mapped_column(default="")  # UserLastName
    user_email: Mapped[str] = mapped_column(default="")  # UserEmail
    user_last_login_date: Mapped[datetime] = mapped_column(TIMESTAMPnullable=True)  # UserLastLoginDate

    parts: Mapped[list["Part"]] = relationship("Part", back_populates="program")
    program_status: Mapped[ProgramStatus] = mapped_column(default=ProgramStatus.CREATED)


class WO(Base):
    """Модель номеров заказов на плазменную резку."""

    wo_number: Mapped[str]  # WONumber
    customer_name: Mapped[str]  # CustomerName
    wo_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)  # WODate
    order_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)  # OrderDate
    wo_data_1: Mapped[str] = mapped_column(default="")  # WOData1
    wo_data_2: Mapped[str] = mapped_column(default="")  # WOData2
    date_created: Mapped[datetime] = mapped_column(TIMESTAMP)  # DateCreated

    parts: Mapped[list["Part"]] = relationship("Part", back_populates="wo")
    wo_status: Mapped[WoStatus] = mapped_column(default=WoStatus.CREATED)


class Part(Base):
    """Модель деталей заказа на плазменную резку."""

    wo_numer_id: Mapped[int] = mapped_column(ForeignKey("wo.id"))
    wo_number: Mapped[WO] = relationship("WO", back_populates="parts")

    program_id: Mapped[int] = mapped_column(ForeignKey("program.id"))
    program: Mapped[Program] = relationship("Program", back_populates="parts")

    part_name: Mapped[str]  # PartName
    repeat_id: Mapped[int] = mapped_column(nullable=True)  # RepeatID
    qty_in_process: Mapped[int]  # QtyInProcess
    part_length: Mapped[float]  # PartLength
    part_width: Mapped[float]  # PartWidth
    true_area: Mapped[float]  # TrueArea
    rect_area: Mapped[float]  # RectArea
    true_weight: Mapped[float]  # TrueWeight
    rect_weight: Mapped[float]  # RectWeight
    cutting_time: Mapped[Decimal]  # CuttingTime
    cutting_length: Mapped[float]  # CuttingLength
    pierce_qty: Mapped[int]  # PierceQty
    nested_area: Mapped[float]  # NestedArea
    total_cutting_time: Mapped[Decimal]  # TotalCuttingTime
    master_part_qty: Mapped[int]  # MasterPartQty
    wo_state: Mapped[str]  # WOState
    due_date: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)  # DueDate
    revision_number: Mapped[str]  # RevisionNumber
    pk_pip: Mapped[str]  # PKPip
    part_status: Mapped[PartStatus] = mapped_column(default=PartStatus.UNASSIGNED)
