"""Enums, status values, and Redis cache-key templates / TTLs."""
from enum import StrEnum


class LocationType(StrEnum):
    HUB = "HUB"
    TERMINAL = "TERMINAL"


class DriverStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class VehicleStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    IN_USE = "IN_USE"
    MAINTENANCE = "MAINTENANCE"


class AllocationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"


class ShiftStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ShiftScope(StrEnum):
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"


UNCOMPLETED_AT_SHIFT_END = "UNCOMPLETED_AT_SHIFT_END"


class CacheKeys:
    FLEET_LIVE = "fleet:live"  

    @staticmethod
    def vehicle_location(vehicle_id: int) -> str:
        return f"vehicle:{vehicle_id}:location"

    INVENTORY_ALL = "cache:inventory:all"

    @staticmethod
    def inventory_location(location_id: int) -> str:
        return f"cache:inventory:location:{location_id}"

    @staticmethod
    def shift_active_driver(driver_id: int) -> str:
        return f"shift:active:driver:{driver_id}"

    @staticmethod
    def blocked(date_iso: str) -> str:
        return f"cache:blocked:{date_iso}"

    @staticmethod
    def alloc_lock(vehicle_id: int, date_iso: str) -> str:
        return f"lock:alloc:{vehicle_id}:{date_iso}"
