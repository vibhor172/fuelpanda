from datetime import date, datetime

from app.dependencies.constants import ShiftStatus
from app.schemas.common import ORMModel, TimestampedOut
from app.schemas.order import OrderOut


class ShiftOut(TimestampedOut):
    driver_id: int
    allocation_id: int
    shift_date: date
    status: ShiftStatus
    started_at: datetime | None
    ended_at: datetime | None


class ShiftVehicleOut(ORMModel):
    id: int
    registration_number: str


class ShiftDetailOut(ShiftOut):
    """Shift plus its assigned orders and the allocated vehicle."""

    vehicle: ShiftVehicleOut | None = None
    orders: list[OrderOut] = []
