from datetime import datetime

from sqlalchemy import DateTime, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import BaseModel
from app.dependencies.constants import VehicleStatus


class Vehicle(BaseModel):
    __tablename__ = "vehicles"

    registration_number: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    capacity_gallons: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[VehicleStatus] = mapped_column(
        Enum(VehicleStatus, name="vehicle_status"),
        nullable=False,
        default=VehicleStatus.AVAILABLE,
    )

    last_latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    last_longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
