"""Rule 5 — GPS ingestion during active shifts + write-through read model (§13)."""
from datetime import datetime

from app.core.base_handler import BaseHandler
from app.custom_exceptions.shift_exceptions import ShiftNotFound
from app.custom_exceptions.tracking_exceptions import (
    InvalidCoordinates,
    NoActiveShiftForGps,
)
from app.custom_exceptions.vehicle_exceptions import VehicleNotFound
from app.dependencies.config import get_settings
from app.dependencies.constants import ShiftStatus
from app.dependencies.utils import utcnow
from app.models.gps_location import GpsLocation
from app.repositories.allocation_repository import AllocationRepository
from app.repositories.gps_repository import GpsRepository
from app.repositories.shift_repository import ShiftRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.tracking import GpsIn
from app.services.cache_service import CacheService


class TrackingHandler(BaseHandler):
    def __init__(
        self,
        db,
        repo: GpsRepository,
        shift_repo: ShiftRepository,
        allocation_repo: AllocationRepository,
        vehicle_repo: VehicleRepository,
        cache: CacheService,
    ) -> None:
        super().__init__(db)
        self.repo = repo
        self.shift_repo = shift_repo
        self.allocation_repo = allocation_repo
        self.vehicle_repo = vehicle_repo
        self.cache = cache
        self.location_ttl = get_settings().vehicle_location_ttl

    def ingest(self, shift_id: int, data: GpsIn) -> GpsLocation:
        shift = self.shift_repo.get(shift_id)
        if shift is None:
            raise ShiftNotFound(details={"id": shift_id})
        if shift.status != ShiftStatus.ACTIVE:
            raise NoActiveShiftForGps(details={"shift_id": shift_id, "status": shift.status})

        lat, lng = float(data.latitude), float(data.longitude)
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise InvalidCoordinates(details={"latitude": lat, "longitude": lng})

        allocation = self.allocation_repo.get(shift.allocation_id)
        vehicle = self.vehicle_repo.get(allocation.vehicle_id) if allocation else None
        if vehicle is None:
            raise VehicleNotFound(details={"shift_id": shift_id})

        recorded_at = data.timestamp or utcnow()
        gps = GpsLocation(
            vehicle_id=vehicle.id,
            shift_id=shift_id,
            latitude=data.latitude,
            longitude=data.longitude,
            recorded_at=recorded_at,
        )
        self.repo.create(gps)

        vehicle.last_latitude = data.latitude
        vehicle.last_longitude = data.longitude
        vehicle.last_seen_at = recorded_at
        self.commit()

        self.cache.write_vehicle_location(
            vehicle.id,
            latitude=lat,
            longitude=lng,
            recorded_at=recorded_at.isoformat() if isinstance(recorded_at, datetime) else str(recorded_at),
            shift_id=shift_id,
            driver_id=shift.driver_id,
            location_ttl=self.location_ttl,
        )
        return gps

    def history(
        self,
        vehicle_id: int,
        *,
        from_ts=None,
        to_ts=None,
        limit: int,
        offset: int,
    ) -> list[GpsLocation]:
        if self.vehicle_repo.get(vehicle_id) is None:
            raise VehicleNotFound(details={"id": vehicle_id})
        return self.repo.history(
            vehicle_id, from_ts=from_ts, to_ts=to_ts, limit=limit, offset=offset
        )
