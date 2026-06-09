from sqlalchemy import select

from app.core.base_repository import BaseRepository
from app.models.inventory import Inventory


class InventoryRepository(BaseRepository[Inventory]):
    model = Inventory

    def get_by_location_product(self, location_id: int, product_id: int) -> Inventory | None:
        stmt = select(Inventory).where(
            Inventory.location_id == location_id, Inventory.product_id == product_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_locked(self, location_id: int, product_id: int) -> Inventory | None:
        stmt = (
            select(Inventory)
            .where(Inventory.location_id == location_id, Inventory.product_id == product_id)
            .with_for_update()
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_location(self, location_id: int) -> list[Inventory]:
        stmt = select(Inventory).where(Inventory.location_id == location_id)
        return list(self.db.execute(stmt).scalars().all())

    def list_all(self) -> list[Inventory]:
        stmt = select(Inventory).order_by(Inventory.location_id, Inventory.product_id)
        return list(self.db.execute(stmt).scalars().all())
