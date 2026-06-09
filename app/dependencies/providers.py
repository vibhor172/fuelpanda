"""DI wiring (Factory pattern). Builds repos, services, and handlers per request.

Swapping any of these for a mock in tests is a one-line dependency_overrides call.
"""
import redis
from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.redis_client import get_redis
from app.handlers.allocation_handler import AllocationHandler
from app.handlers.driver_handler import DriverHandler
from app.handlers.fleet_handler import FleetHandler
from app.handlers.inventory_handler import InventoryHandler
from app.handlers.location_handler import LocationHandler
from app.handlers.order_handler import OrderHandler
from app.handlers.product_handler import ProductHandler
from app.handlers.shift_handler import ShiftHandler
from app.handlers.tracking_handler import TrackingHandler
from app.handlers.vehicle_handler import VehicleHandler
from app.repositories.allocation_repository import AllocationRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.gps_repository import GpsRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.shift_repository import ShiftRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.services.cache_service import CacheService
from app.services.fleet_status_service import FleetStatusService
from app.services.lock_service import LockService


def get_cache_service(r: redis.Redis = Depends(get_redis)) -> CacheService:
    return CacheService(r)


def get_lock_service(r: redis.Redis = Depends(get_redis)) -> LockService:
    return LockService(r)


def get_fleet_status_service(
    r: redis.Redis = Depends(get_redis),
    cache: CacheService = Depends(get_cache_service),
) -> FleetStatusService:
    return FleetStatusService(r, cache)


def get_location_handler(db: Session = Depends(get_db)) -> LocationHandler:
    return LocationHandler(db, LocationRepository(db))


def get_product_handler(db: Session = Depends(get_db)) -> ProductHandler:
    return ProductHandler(db, ProductRepository(db))


def get_inventory_handler(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> InventoryHandler:
    return InventoryHandler(
        db,
        InventoryRepository(db),
        LocationRepository(db),
        ProductRepository(db),
        cache,
    )


def get_driver_handler(db: Session = Depends(get_db)) -> DriverHandler:
    return DriverHandler(db, DriverRepository(db))


def get_vehicle_handler(db: Session = Depends(get_db)) -> VehicleHandler:
    return VehicleHandler(db, VehicleRepository(db))


def get_allocation_handler(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
    lock: LockService = Depends(get_lock_service),
) -> AllocationHandler:
    return AllocationHandler(
        db,
        AllocationRepository(db),
        VehicleRepository(db),
        DriverRepository(db),
        ShiftRepository(db),
        cache,
        lock,
    )


def get_shift_handler(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> ShiftHandler:
    return ShiftHandler(
        db,
        ShiftRepository(db),
        AllocationRepository(db),
        OrderRepository(db),
        VehicleRepository(db),
        cache,
    )


def get_order_handler(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> OrderHandler:
    return OrderHandler(
        db,
        OrderRepository(db),
        ShiftRepository(db),
        LocationRepository(db),
        ProductRepository(db),
        InventoryRepository(db),
        cache,
    )


def get_tracking_handler(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache_service),
) -> TrackingHandler:
    return TrackingHandler(
        db,
        GpsRepository(db),
        ShiftRepository(db),
        AllocationRepository(db),
        VehicleRepository(db),
        cache,
    )


def get_fleet_handler(
    db: Session = Depends(get_db),
    fleet_service: FleetStatusService = Depends(get_fleet_status_service),
) -> FleetHandler:
    return FleetHandler(db, VehicleRepository(db), fleet_service)
