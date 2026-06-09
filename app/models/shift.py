from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import BaseModel
from app.dependencies.constants import ShiftStatus


class Shift(BaseModel):
    __tablename__ = "shifts"

    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    allocation_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle_allocations.id"), nullable=False
    )
    shift_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ShiftStatus] = mapped_column(
        Enum(ShiftStatus, name="shift_status"),
        nullable=False,
        default=ShiftStatus.SCHEDULED,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    allocation = relationship("VehicleAllocation")
    orders = relationship("Order", back_populates="shift")

    __table_args__ = (
        UniqueConstraint("driver_id", "shift_date", name="uq_shift_driver_date"),
    )
