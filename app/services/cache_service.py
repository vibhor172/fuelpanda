"""Cache-aside + write-through helpers. Redis is a rebuildable accelerator;
Postgres is always the source of truth (context.md §12)."""
import json
from typing import Any

from app.core.base_service import BaseService
from app.dependencies.constants import CacheKeys


class CacheService(BaseService):
    def get_json(self, key: str) -> Any | None:
        raw = self.redis.get(key)
        return json.loads(raw) if raw else None

    def set_json(self, key: str, value: Any, ttl: int) -> None:
        self.redis.set(key, json.dumps(value, default=str), ex=ttl)

    def delete(self, *keys: str) -> None:
        if keys:
            self.redis.delete(*keys)

    def invalidate_inventory(self, location_id: int) -> None:
        self.delete(CacheKeys.INVENTORY_ALL, CacheKeys.inventory_location(location_id))

    def invalidate_inventory_all(self) -> None:
        self.delete(CacheKeys.INVENTORY_ALL)

    def write_vehicle_location(
        self,
        vehicle_id: int,
        *,
        latitude: float,
        longitude: float,
        recorded_at: str,
        shift_id: int,
        driver_id: int,
        location_ttl: int,
    ) -> None:
        payload = {
            "vehicle_id": vehicle_id,
            "latitude": latitude,
            "longitude": longitude,
            "recorded_at": recorded_at,
            "shift_id": shift_id,
            "driver_id": driver_id,
        }
        encoded = json.dumps(payload, default=str)
        self.redis.hset(CacheKeys.FLEET_LIVE, str(vehicle_id), encoded)
        self.redis.set(CacheKeys.vehicle_location(vehicle_id), encoded, ex=location_ttl)

    def read_fleet_live(self) -> list[dict[str, Any]]:
        raw = self.redis.hgetall(CacheKeys.FLEET_LIVE)
        return [json.loads(v) for v in raw.values()]

    def read_vehicle_location(self, vehicle_id: int) -> dict[str, Any] | None:
        raw = self.redis.get(CacheKeys.vehicle_location(vehicle_id))
        return json.loads(raw) if raw else None

    def set_active_shift(self, driver_id: int, shift_id: int) -> None:
        self.redis.set(CacheKeys.shift_active_driver(driver_id), str(shift_id))

    def get_active_shift(self, driver_id: int) -> int | None:
        raw = self.redis.get(CacheKeys.shift_active_driver(driver_id))
        return int(raw) if raw else None

    def clear_active_shift(self, driver_id: int) -> None:
        self.delete(CacheKeys.shift_active_driver(driver_id))

    def remove_from_fleet(self, vehicle_id: int) -> None:
        self.redis.hdel(CacheKeys.FLEET_LIVE, str(vehicle_id))
        self.delete(CacheKeys.vehicle_location(vehicle_id))

    def add_blocked_vehicle(self, date_iso: str, vehicle_id: int, ttl: int) -> None:
        key = CacheKeys.blocked(date_iso)
        self.redis.sadd(key, vehicle_id)
        self.redis.expire(key, ttl)

    def remove_blocked_vehicle(self, date_iso: str, vehicle_id: int) -> None:
        self.redis.srem(CacheKeys.blocked(date_iso), vehicle_id)

    def is_blocked(self, date_iso: str, vehicle_id: int) -> bool:
        return bool(self.redis.sismember(CacheKeys.blocked(date_iso), vehicle_id))
