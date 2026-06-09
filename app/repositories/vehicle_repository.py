from sqlalchemy import select

from app.core.base_repository import BaseRepository
from app.dependencies.constants import ShiftStatus
from app.models.shift import Shift
from app.models.vehicle import Vehicle
from app.models.vehicle_allocation import VehicleAllocation


class VehicleRepository(BaseRepository[Vehicle]):
    model = Vehicle

    def list_active(self) -> list[Vehicle]:
        """Vehicles tied to an ACTIVE shift with a known last position.

        DB-side fallback for fleet status (context.md §13) — one indexed pass,
        never a scan of gps_locations history.
        """
        stmt = (
            select(Vehicle)
            .join(VehicleAllocation, VehicleAllocation.vehicle_id == Vehicle.id)
            .join(Shift, Shift.allocation_id == VehicleAllocation.id)
            .where(Shift.status == ShiftStatus.ACTIVE)
            .where(Vehicle.last_seen_at.is_not(None))
        )
        return list(self.db.execute(stmt).scalars().unique().all())
