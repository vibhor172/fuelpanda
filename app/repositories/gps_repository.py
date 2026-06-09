from datetime import datetime

from sqlalchemy import select

from app.core.base_repository import BaseRepository
from app.models.gps_location import GpsLocation


class GpsRepository(BaseRepository[GpsLocation]):
    model = GpsLocation

    def history(
        self,
        vehicle_id: int,
        *,
        from_ts: datetime | None = None,
        to_ts: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[GpsLocation]:
        """Partition-pruned, indexed range scan over (vehicle_id, recorded_at DESC)."""
        stmt = select(GpsLocation).where(GpsLocation.vehicle_id == vehicle_id)
        if from_ts is not None:
            stmt = stmt.where(GpsLocation.recorded_at >= from_ts)
        if to_ts is not None:
            stmt = stmt.where(GpsLocation.recorded_at <= to_ts)
        stmt = stmt.order_by(GpsLocation.recorded_at.desc()).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())
