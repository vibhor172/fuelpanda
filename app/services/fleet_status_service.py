"""Assembles the fleet-status read model (context.md §13).

Hot path: HGETALL fleet:live → O(active vehicles), no history scan.
Cold path: denormalized vehicles.last_* columns, one indexed pass.
"""
from app.core.base_service import BaseService
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.fleet import FleetStatusOut, VehicleLocation
from app.services.cache_service import CacheService


class FleetStatusService(BaseService):
    def __init__(self, redis_client, cache: CacheService) -> None:
        super().__init__(redis_client)
        self.cache = cache

    def get_status(self, vehicle_repo: VehicleRepository) -> FleetStatusOut:
        live = self.cache.read_fleet_live()
        if live:
            vehicles = [
                VehicleLocation(
                    vehicle_id=int(v["vehicle_id"]),
                    latitude=float(v["latitude"]),
                    longitude=float(v["longitude"]),
                    recorded_at=v.get("recorded_at"),
                    shift_id=v.get("shift_id"),
                    driver_id=v.get("driver_id"),
                )
                for v in live
            ]
            return FleetStatusOut(source="redis", count=len(vehicles), vehicles=vehicles)

        rows = vehicle_repo.list_active()
        vehicles = [
            VehicleLocation(
                vehicle_id=v.id,
                latitude=float(v.last_latitude),
                longitude=float(v.last_longitude),
                recorded_at=v.last_seen_at,
            )
            for v in rows
        ]
        return FleetStatusOut(source="db", count=len(vehicles), vehicles=vehicles)

    def get_vehicle_location(
        self, vehicle_id: int, vehicle_repo: VehicleRepository
    ) -> VehicleLocation | None:
        cached = self.cache.read_vehicle_location(vehicle_id)
        if cached:
            return VehicleLocation(
                vehicle_id=int(cached["vehicle_id"]),
                latitude=float(cached["latitude"]),
                longitude=float(cached["longitude"]),
                recorded_at=cached.get("recorded_at"),
                shift_id=cached.get("shift_id"),
                driver_id=cached.get("driver_id"),
            )
        vehicle = vehicle_repo.get(vehicle_id)
        if vehicle is None or vehicle.last_seen_at is None:
            return None
        return VehicleLocation(
            vehicle_id=vehicle.id,
            latitude=float(vehicle.last_latitude),
            longitude=float(vehicle.last_longitude),
            recorded_at=vehicle.last_seen_at,
        )
