from pydantic import BaseModel, Field

from app.dependencies.constants import DriverStatus
from app.schemas.common import TimestampedOut


class DriverCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    license_number: str = Field(min_length=1, max_length=64)
    phone: str | None = Field(default=None, max_length=32)
    status: DriverStatus = DriverStatus.ACTIVE


class DriverUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    license_number: str | None = Field(default=None, min_length=1, max_length=64)
    phone: str | None = Field(default=None, max_length=32)
    status: DriverStatus | None = None


class DriverOut(TimestampedOut):
    name: str
    license_number: str
    phone: str | None
    status: DriverStatus
