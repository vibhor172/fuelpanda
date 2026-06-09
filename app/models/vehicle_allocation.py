from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import BaseModel
from app.dependencies.constants import AllocationStatus


class VehicleAllocation(BaseModel):
    __tablename__ = "vehicle_allocations"

    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(ForeignKey("drivers.id"), nullable=False)
    allocation_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[AllocationStatus] = mapped_column(
        Enum(AllocationStatus, name="allocation_status"),
        nullable=False,
        default=AllocationStatus.ACTIVE,
    )

    __table_args__ = (
        Index(
            "uq_alloc_vehicle_date_active",
            "vehicle_id",
            "allocation_date",
            unique=True,
            postgresql_where=text("status = 'ACTIVE'"),
            sqlite_where=text("status = 'ACTIVE'"),
        ),
        Index(
            "uq_alloc_driver_date_active",
            "driver_id",
            "allocation_date",
            unique=True,
            postgresql_where=text("status = 'ACTIVE'"),
            sqlite_where=text("status = 'ACTIVE'"),
        ),
    )
