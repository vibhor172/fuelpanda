from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import BaseModel
from app.dependencies.constants import DriverStatus


class Driver(BaseModel):
    __tablename__ = "drivers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    license_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[DriverStatus] = mapped_column(
        Enum(DriverStatus, name="driver_status"),
        nullable=False,
        default=DriverStatus.ACTIVE,
    )
