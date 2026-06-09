from datetime import date

from pydantic import BaseModel

from app.dependencies.constants import AllocationStatus
from app.schemas.common import TimestampedOut


class AllocationCreate(BaseModel):
    vehicle_id: int
    driver_id: int
    allocation_date: date


class AllocationOut(TimestampedOut):
    vehicle_id: int
    driver_id: int
    allocation_date: date
    status: AllocationStatus
