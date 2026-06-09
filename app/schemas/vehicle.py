from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.dependencies.constants import VehicleStatus
from app.schemas.common import TimestampedOut


class VehicleCreate(BaseModel):
    registration_number: str = Field(min_length=1, max_length=64)
    capacity_gallons: Decimal = Field(gt=0)
    status: VehicleStatus = VehicleStatus.AVAILABLE


class VehicleUpdate(BaseModel):
    registration_number: str | None = Field(default=None, min_length=1, max_length=64)
    capacity_gallons: Decimal | None = Field(default=None, gt=0)
    status: VehicleStatus | None = None


class VehicleOut(TimestampedOut):
    registration_number: str
    capacity_gallons: Decimal
    status: VehicleStatus
    last_latitude: Decimal | None
    last_longitude: Decimal | None
    last_seen_at: datetime | None
