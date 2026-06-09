from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.dependencies.constants import OrderStatus
from app.schemas.common import ORMModel, TimestampedOut


class OrderItemIn(BaseModel):
    product_id: int
    quantity_gallons: Decimal = Field(gt=0)


class OrderCreate(BaseModel):
    shift_id: int
    destination_id: int
    items: list[OrderItemIn] = Field(min_length=1)


class OrderUpdate(BaseModel):
    destination_id: int | None = None
    items: list[OrderItemIn] | None = Field(default=None, min_length=1)


class OrderFail(BaseModel):
    reason: str = Field(min_length=1)


class OrderItemOut(ORMModel):
    id: int
    product_id: int
    quantity_gallons: Decimal


class OrderOut(TimestampedOut):
    shift_id: int
    destination_id: int
    status: OrderStatus
    failure_reason: str | None
    completed_at: datetime | None
    items: list[OrderItemOut] = []
