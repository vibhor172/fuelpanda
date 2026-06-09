from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class GpsIn(BaseModel):
    latitude: Decimal = Field(ge=-90, le=90)
    longitude: Decimal = Field(ge=-180, le=180)
    timestamp: datetime | None = None


class GpsOut(ORMModel):
    id: int
    vehicle_id: int
    shift_id: int
    latitude: Decimal
    longitude: Decimal
    recorded_at: datetime
