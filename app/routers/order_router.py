from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_current_admin, get_current_driver
from app.dependencies.providers import get_order_handler
from app.handlers.order_handler import OrderHandler
from app.schemas.order import OrderCreate, OrderFail, OrderOut, OrderUpdate

router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(get_current_admin)])


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, handler: OrderHandler = Depends(get_order_handler)):
    return handler.create(payload)


@router.put("/{order_id}", response_model=OrderOut)
def update_order(
    order_id: int, payload: OrderUpdate, handler: OrderHandler = Depends(get_order_handler)
):
    return handler.update(order_id, payload)


@router.get("", response_model=list[OrderOut])
def list_orders(
    shift_id: int | None = Query(default=None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    handler: OrderHandler = Depends(get_order_handler),
):
    return handler.list(shift_id=shift_id, limit=limit, offset=offset)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, handler: OrderHandler = Depends(get_order_handler)):
    return handler.get(order_id)


driver_router = APIRouter(
    prefix="/driver/orders", tags=["deliveries"], dependencies=[Depends(get_current_driver)]
)


@driver_router.post("/{order_id}/complete", response_model=OrderOut)
def complete_delivery(order_id: int, handler: OrderHandler = Depends(get_order_handler)):
    return handler.complete(order_id)


@driver_router.post("/{order_id}/fail", response_model=OrderOut)
def fail_delivery(
    order_id: int, payload: OrderFail, handler: OrderHandler = Depends(get_order_handler)
):
    return handler.fail(order_id, payload.reason)
