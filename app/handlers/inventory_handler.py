from app.core.base_handler import BaseHandler
from app.custom_exceptions.inventory_exceptions import InventoryNotFound
from app.custom_exceptions.location_exceptions import LocationNotFound
from app.custom_exceptions.product_exceptions import ProductNotFound
from app.dependencies.config import get_settings
from app.dependencies.constants import CacheKeys
from app.models.inventory import Inventory
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.inventory import InventoryCreate, InventoryUpdate
from app.services.cache_service import CacheService


def _serialize(inv: Inventory) -> dict:
    return {
        "id": inv.id,
        "location_id": inv.location_id,
        "product_id": inv.product_id,
        "quantity_gallons": str(inv.quantity_gallons),
    }


class InventoryHandler(BaseHandler):
    def __init__(
        self,
        db,
        repo: InventoryRepository,
        location_repo: LocationRepository,
        product_repo: ProductRepository,
        cache: CacheService,
    ) -> None:
        super().__init__(db)
        self.repo = repo
        self.location_repo = location_repo
        self.product_repo = product_repo
        self.cache = cache
        self.ttl = get_settings().inventory_cache_ttl

    def create(self, data: InventoryCreate) -> Inventory:
        if self.location_repo.get(data.location_id) is None:
            raise LocationNotFound(details={"id": data.location_id})
        if self.product_repo.get(data.product_id) is None:
            raise ProductNotFound(details={"id": data.product_id})
        inv = Inventory(**data.model_dump())
        self.repo.create(inv)
        self.commit()
        self.cache.invalidate_inventory(inv.location_id)
        return inv

    def update(self, inventory_id: int, data: InventoryUpdate) -> Inventory:
        inv = self._get(inventory_id)
        self.repo.update(inv, data.model_dump(exclude_unset=True))
        self.commit()
        self.cache.invalidate_inventory(inv.location_id)
        return inv

    def list_all(self) -> list[dict]:
        """Monitor inventories across all locations (cache-aside, §13)."""
        cached = self.cache.get_json(CacheKeys.INVENTORY_ALL)
        if cached is not None:
            return cached
        rows = [_serialize(i) for i in self.repo.list_all()]
        self.cache.set_json(CacheKeys.INVENTORY_ALL, rows, self.ttl)
        return rows

    def list_for_location(self, location_id: int) -> list[dict]:
        if self.location_repo.get(location_id) is None:
            raise LocationNotFound(details={"id": location_id})
        key = CacheKeys.inventory_location(location_id)
        cached = self.cache.get_json(key)
        if cached is not None:
            return cached
        rows = [_serialize(i) for i in self.repo.list_by_location(location_id)]
        self.cache.set_json(key, rows, self.ttl)
        return rows

    def _get(self, inventory_id: int) -> Inventory:
        inv = self.repo.get(inventory_id)
        if inv is None:
            raise InventoryNotFound(details={"id": inventory_id})
        return inv
