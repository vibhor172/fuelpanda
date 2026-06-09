"""Rule 3 — shift lifecycle (start / end) and scoped listing (context.md §11)."""
from app.core.base_handler import BaseHandler
from app.custom_exceptions.allocation_exceptions import AllocationNotFound
from app.custom_exceptions.shift_exceptions import (
    InvalidShiftTransition,
    NoAllocationForShift,
    ShiftNotActive,
    ShiftNotFound,
)
from app.dependencies.constants import (
    UNCOMPLETED_AT_SHIFT_END,
    AllocationStatus,
    OrderStatus,
    ShiftScope,
    ShiftStatus,
    VehicleStatus,
)
from app.dependencies.utils import today, utcnow
from app.models.shift import Shift
from app.repositories.allocation_repository import AllocationRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.shift_repository import ShiftRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.services.cache_service import CacheService


class ShiftHandler(BaseHandler):
    def __init__(
        self,
        db,
        repo: ShiftRepository,
        allocation_repo: AllocationRepository,
        order_repo: OrderRepository,
        vehicle_repo: VehicleRepository,
        cache: CacheService,
    ) -> None:
        super().__init__(db)
        self.repo = repo
        self.allocation_repo = allocation_repo
        self.order_repo = order_repo
        self.vehicle_repo = vehicle_repo
        self.cache = cache

    def list_for_driver(self, driver_id: int, scope: ShiftScope) -> list[Shift]:
        now = today()
        if scope == ShiftScope.PAST:
            return self.repo.list_for_driver(driver_id, date_lt=now)
        if scope == ShiftScope.FUTURE:
            return self.repo.list_for_driver(driver_id, date_gt=now)
        return self.repo.list_for_driver(driver_id, date_eq=now)

    def get(self, shift_id: int) -> Shift:
        return self._get(shift_id)

    def vehicle_for(self, shift: Shift):
        """Resolve the vehicle allocated to this shift (for detail responses)."""
        allocation = self.allocation_repo.get(shift.allocation_id)
        if allocation is None:
            return None
        return self.vehicle_repo.get(allocation.vehicle_id)

    def start(self, shift_id: int) -> Shift:
        shift = self._get(shift_id)
        if shift.status == ShiftStatus.ACTIVE:
            raise InvalidShiftTransition(details={"id": shift_id, "status": shift.status})
        if shift.status != ShiftStatus.SCHEDULED:
            raise InvalidShiftTransition(details={"id": shift_id, "status": shift.status})

        allocation = self.allocation_repo.get_active_for_driver_date(
            shift.driver_id, shift.shift_date
        )
        if allocation is None:
            raise NoAllocationForShift(details={"shift_id": shift_id})

        shift.status = ShiftStatus.ACTIVE
        shift.started_at = utcnow()
        self.commit()

        self.cache.set_active_shift(shift.driver_id, shift.id)
        return shift

    def end(self, shift_id: int) -> Shift:
        shift = self._get(shift_id)
        if shift.status != ShiftStatus.ACTIVE:
            raise ShiftNotActive(details={"id": shift_id, "status": shift.status})

        for order in self.order_repo.list_open_for_shift(shift_id):
            order.status = OrderStatus.FAILED
            order.failure_reason = UNCOMPLETED_AT_SHIFT_END

        shift.status = ShiftStatus.COMPLETED
        shift.ended_at = utcnow()

        allocation = self.allocation_repo.get(shift.allocation_id)
        if allocation is None:
            raise AllocationNotFound(details={"id": shift.allocation_id})
        allocation.status = AllocationStatus.RELEASED

        vehicle = self.vehicle_repo.get(allocation.vehicle_id)
        if vehicle is not None:
            vehicle.status = VehicleStatus.AVAILABLE

        self.commit()

        self.cache.clear_active_shift(shift.driver_id)
        if vehicle is not None:
            self.cache.remove_from_fleet(vehicle.id)
        self.cache.remove_blocked_vehicle(allocation.allocation_date.isoformat(), allocation.vehicle_id)
        return shift

    def _get(self, shift_id: int) -> Shift:
        shift = self.repo.get(shift_id)
        if shift is None:
            raise ShiftNotFound(details={"id": shift_id})
        return shift
