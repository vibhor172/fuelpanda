"""Rule 2 — inventory consistency on delivery (context.md §11).

complete() runs in ONE transaction with row locks on the order and on each
inventory row, so the delivery + all inventory bumps are atomic.
"""
from app.core.base_handler import BaseHandler
from app.custom_exceptions.location_exceptions import LocationNotFound
from app.custom_exceptions.order_exceptions import (
    DeliveryAlreadyFinalized,
    InvalidOrderStatus,
    MissingFailureReason,
    OrderNotFound,
)
from app.custom_exceptions.product_exceptions import ProductNotFound
from app.custom_exceptions.shift_exceptions import ShiftNotActive, ShiftNotFound
from app.dependencies.constants import OrderStatus, ShiftStatus
from app.dependencies.utils import utcnow
from app.models.inventory import Inventory
from app.models.order import Order, OrderItem
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.location_repository import LocationRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.shift_repository import ShiftRepository
from app.schemas.order import OrderCreate, OrderUpdate
from app.services.cache_service import CacheService

_FINALIZED = {OrderStatus.COMPLETED, OrderStatus.FAILED}


class OrderHandler(BaseHandler):
    def __init__(
        self,
        db,
        repo: OrderRepository,
        shift_repo: ShiftRepository,
        location_repo: LocationRepository,
        product_repo: ProductRepository,
        inventory_repo: InventoryRepository,
        cache: CacheService,
    ) -> None:
        super().__init__(db)
        self.repo = repo
        self.shift_repo = shift_repo
        self.location_repo = location_repo
        self.product_repo = product_repo
        self.inventory_repo = inventory_repo
        self.cache = cache

    def create(self, data: OrderCreate) -> Order:
        shift = self.shift_repo.get(data.shift_id)
        if shift is None:
            raise ShiftNotFound(details={"id": data.shift_id})
        if shift.status == ShiftStatus.COMPLETED:
            raise InvalidOrderStatus("Cannot add orders to a completed shift")
        if self.location_repo.get(data.destination_id) is None:
            raise LocationNotFound(details={"id": data.destination_id})
        self._validate_products(data.items)

        order = Order(
            shift_id=data.shift_id,
            destination_id=data.destination_id,
            status=OrderStatus.PENDING,
            items=[
                OrderItem(product_id=i.product_id, quantity_gallons=i.quantity_gallons)
                for i in data.items
            ],
        )
        self.repo.create(order)
        self.commit()
        return order

    def update(self, order_id: int, data: OrderUpdate) -> Order:
        order = self._get(order_id)
        if order.status != OrderStatus.PENDING:
            raise InvalidOrderStatus(
                "Orders can only be edited before the delivery starts",
                details={"id": order_id, "status": order.status},
            )
        if data.destination_id is not None:
            if self.location_repo.get(data.destination_id) is None:
                raise LocationNotFound(details={"id": data.destination_id})
            order.destination_id = data.destination_id
        if data.items is not None:
            self._validate_products(data.items)
            order.items = [
                OrderItem(product_id=i.product_id, quantity_gallons=i.quantity_gallons)
                for i in data.items
            ]
        self.commit()
        return order

    def get(self, order_id: int) -> Order:
        return self._get(order_id)

    def list(self, *, shift_id: int | None = None, limit: int, offset: int) -> list[Order]:
        if shift_id is not None:
            return self.repo.list_for_shift(shift_id)
        return self.repo.list(limit=limit, offset=offset)

    def complete(self, order_id: int) -> Order:
        order = self.repo.get_for_update(order_id)
        if order is None:
            raise OrderNotFound(details={"id": order_id})
        if order.status in _FINALIZED:
            raise DeliveryAlreadyFinalized(details={"id": order_id, "status": order.status})

        shift = self.shift_repo.get(order.shift_id)
        if shift is None or shift.status != ShiftStatus.ACTIVE:
            raise ShiftNotActive(details={"shift_id": order.shift_id})

        for item in order.items:
            inv = self.inventory_repo.get_locked(order.destination_id, item.product_id)
            if inv is None:
                inv = Inventory(
                    location_id=order.destination_id,
                    product_id=item.product_id,
                    quantity_gallons=item.quantity_gallons,
                )
                self.inventory_repo.create(inv)
            else:
                inv.quantity_gallons = inv.quantity_gallons + item.quantity_gallons

        order.status = OrderStatus.COMPLETED
        order.completed_at = utcnow()
        self.commit()

        self.cache.invalidate_inventory(order.destination_id)
        return order

    def fail(self, order_id: int, reason: str) -> Order:
        if not reason or not reason.strip():
            raise MissingFailureReason()
        order = self.repo.get_for_update(order_id)
        if order is None:
            raise OrderNotFound(details={"id": order_id})
        if order.status in _FINALIZED:
            raise DeliveryAlreadyFinalized(details={"id": order_id, "status": order.status})

        order.status = OrderStatus.FAILED
        order.failure_reason = reason.strip()
        self.commit()
        return order

    def _validate_products(self, items) -> None:
        for item in items:
            if self.product_repo.get(item.product_id) is None:
                raise ProductNotFound(details={"id": item.product_id})

    def _get(self, order_id: int) -> Order:
        order = self.repo.get(order_id)
        if order is None:
            raise OrderNotFound(details={"id": order_id})
        return order
