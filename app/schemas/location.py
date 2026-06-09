from decimal import Decimal

from pydantic import BaseModel, Field

from app.dependencies.constants import LocationType
from app.schemas.common import TimestampedOut


class LocationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: LocationType
    address: str | None = None
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)


class LocationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: LocationType | None = None
    address: str | None = None
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)


class LocationOut(TimestampedOut):
    name: str
    type: LocationType
    address: str | None
    latitude: Decimal | None
    longitude: Decimal | None
