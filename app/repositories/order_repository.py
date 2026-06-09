from sqlalchemy import select

from app.core.base_repository import BaseRepository
from app.dependencies.constants import OrderStatus
from app.models.order import Order


class OrderRepository(BaseRepository[Order]):
    model = Order

    def list_open_for_shift(self, shift_id: int) -> list[Order]:
        """Orders still PENDING / IN_PROGRESS for a shift (auto-failed on shift end)."""
        stmt = select(Order).where(
            Order.shift_id == shift_id,
            Order.status.in_([OrderStatus.PENDING, OrderStatus.IN_PROGRESS]),
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_for_shift(self, shift_id: int) -> list[Order]:
        stmt = select(Order).where(Order.shift_id == shift_id).order_by(Order.id)
        return list(self.db.execute(stmt).scalars().all())
