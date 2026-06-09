from datetime import date

from sqlalchemy import select

from app.core.base_repository import BaseRepository
from app.dependencies.constants import AllocationStatus
from app.models.vehicle_allocation import VehicleAllocation


class AllocationRepository(BaseRepository[VehicleAllocation]):
    model = VehicleAllocation

    def get_active_for_driver_date(
        self, driver_id: int, allocation_date: date
    ) -> VehicleAllocation | None:
        stmt = select(VehicleAllocation).where(
            VehicleAllocation.driver_id == driver_id,
            VehicleAllocation.allocation_date == allocation_date,
            VehicleAllocation.status == AllocationStatus.ACTIVE,
        )
        return self.db.execute(stmt).scalars().first()

    def list_filtered(
        self,
        *,
        allocation_date: date | None = None,
        vehicle_id: int | None = None,
        driver_id: int | None = None,
    ) -> list[VehicleAllocation]:
        stmt = select(VehicleAllocation)
        if allocation_date is not None:
            stmt = stmt.where(VehicleAllocation.allocation_date == allocation_date)
        if vehicle_id is not None:
            stmt = stmt.where(VehicleAllocation.vehicle_id == vehicle_id)
        if driver_id is not None:
            stmt = stmt.where(VehicleAllocation.driver_id == driver_id)
        stmt = stmt.order_by(VehicleAllocation.id)
        return list(self.db.execute(stmt).scalars().all())
