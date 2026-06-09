from datetime import date

from sqlalchemy import select

from app.core.base_repository import BaseRepository
from app.models.shift import Shift


class ShiftRepository(BaseRepository[Shift]):
    model = Shift

    def list_for_driver(
        self,
        driver_id: int,
        *,
        date_lt: date | None = None,
        date_eq: date | None = None,
        date_gt: date | None = None,
    ) -> list[Shift]:
        stmt = select(Shift).where(Shift.driver_id == driver_id)
        if date_lt is not None:
            stmt = stmt.where(Shift.shift_date < date_lt)
        if date_eq is not None:
            stmt = stmt.where(Shift.shift_date == date_eq)
        if date_gt is not None:
            stmt = stmt.where(Shift.shift_date > date_gt)
        stmt = stmt.order_by(Shift.shift_date)
        return list(self.db.execute(stmt).scalars().all())
