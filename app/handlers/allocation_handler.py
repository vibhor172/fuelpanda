"""Rule 1 — vehicle allocation (one vehicle, one driver, per day).

Enforcement = DB unique partial index (authoritative). The Redis lock is
defense-in-depth only; correctness never depends on it (context.md §11).
"""
from sqlalchemy.exc import IntegrityError

from app.core.base_handler import BaseHandler
from app.custom_exceptions.allocation_exceptions import (
    AllocationConflict,
    AllocationNotFound,
    VehicleAlreadyAllocated,
)
from app.custom_exceptions.driver_exceptions import DriverInactive, DriverNotFound
from app.custom_exceptions.vehicle_exceptions import VehicleNotFound, VehicleUnavailable
from app.dependencies.config import get_settings
from app.dependencies.constants import (
    AllocationStatus,
    CacheKeys,
    DriverStatus,
    ShiftStatus,
    VehicleStatus,
)
from app.models.shift import Shift
from app.models.vehicle_allocation import VehicleAllocation
from app.repositories.allocation_repository import AllocationRepository
from app.repositories.driver_repository import DriverRepository
from app.repositories.shift_repository import ShiftRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.allocation import AllocationCreate
from app.services.cache_service import CacheService
from app.services.lock_service import LockService


class AllocationHandler(BaseHandler):
    def __init__(
        self,
        db,
        repo: AllocationRepository,
        vehicle_repo: VehicleRepository,
        driver_repo: DriverRepository,
        shift_repo: ShiftRepository,
        cache: CacheService,
        lock: LockService,
    ) -> None:
        super().__init__(db)
        self.repo = repo
        self.vehicle_repo = vehicle_repo
        self.driver_repo = driver_repo
        self.shift_repo = shift_repo
        self.cache = cache
        self.lock = lock
        self.settings = get_settings()

    def allocate(self, data: AllocationCreate) -> VehicleAllocation:
        date_iso = data.allocation_date.isoformat()
        lock_key = CacheKeys.alloc_lock(data.vehicle_id, date_iso)

        with self.lock.acquire(lock_key, self.settings.alloc_lock_ttl):
          
            vehicle = self.vehicle_repo.get(data.vehicle_id)
            if vehicle is None:
                raise VehicleNotFound(details={"id": data.vehicle_id})
            if vehicle.status == VehicleStatus.MAINTENANCE:
                raise VehicleUnavailable(details={"id": vehicle.id, "status": vehicle.status})

            driver = self.driver_repo.get(data.driver_id)
            if driver is None:
                raise DriverNotFound(details={"id": data.driver_id})
            if driver.status != DriverStatus.ACTIVE:
                raise DriverInactive(details={"id": driver.id})

            allocation = VehicleAllocation(
                vehicle_id=data.vehicle_id,
                driver_id=data.driver_id,
                allocation_date=data.allocation_date,
                status=AllocationStatus.ACTIVE,
            )
            try:
                self.repo.create(allocation)
                self.db.flush()
            except IntegrityError:
                self.rollback()
                raise VehicleAlreadyAllocated(
                    details={"vehicle_id": data.vehicle_id, "date": date_iso}
                ) from None

            vehicle.status = VehicleStatus.IN_USE
            shift = Shift(
                driver_id=data.driver_id,
                allocation_id=allocation.id,
                shift_date=data.allocation_date,
                status=ShiftStatus.SCHEDULED,
            )
            self.shift_repo.create(shift)
            self.commit()

        self.cache.add_blocked_vehicle(date_iso, data.vehicle_id, ttl=86400)
        return allocation

    def list(
        self, *, allocation_date=None, vehicle_id=None, driver_id=None
    ) -> list[VehicleAllocation]:
        return self.repo.list_filtered(
            allocation_date=allocation_date, vehicle_id=vehicle_id, driver_id=driver_id
        )

    def release(self, allocation_id: int) -> None:
        """Release an allocation: free the vehicle. Only if the shift hasn't started."""
        allocation = self.repo.get(allocation_id)
        if allocation is None:
            raise AllocationNotFound(details={"id": allocation_id})
        if allocation.status != AllocationStatus.ACTIVE:
            raise AllocationConflict(details={"id": allocation_id, "status": allocation.status})

        shift = self.shift_repo.list(allocation_id=allocation_id)
        shift = shift[0] if shift else None
        if shift is not None and shift.status != ShiftStatus.SCHEDULED:
            raise AllocationConflict(
                "Cannot release an allocation whose shift has already started",
                details={"id": allocation_id, "shift_status": shift.status},
            )

        allocation.status = AllocationStatus.RELEASED

        if shift is not None:
            self.shift_repo.delete(shift)
        vehicle = self.vehicle_repo.get(allocation.vehicle_id)
        if vehicle is not None and vehicle.status == VehicleStatus.IN_USE:
            vehicle.status = VehicleStatus.AVAILABLE
        self.commit()

        self.cache.remove_blocked_vehicle(allocation.allocation_date.isoformat(), allocation.vehicle_id)
