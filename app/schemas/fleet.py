from datetime import datetime

from pydantic import BaseModel


class VehicleLocation(BaseModel):
    vehicle_id: int
    latitude: float
    longitude: float
    recorded_at: datetime | None = None
    shift_id: int | None = None
    driver_id: int | None = None


class FleetStatusOut(BaseModel):
    source: str
    count: int
    vehicles: list[VehicleLocation]
