from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedOut


class InventoryCreate(BaseModel):
    location_id: int
    product_id: int
    quantity_gallons: Decimal = Field(ge=0)


class InventoryUpdate(BaseModel):
    quantity_gallons: Decimal = Field(ge=0)


class InventoryOut(TimestampedOut):
    location_id: int
    product_id: int
    quantity_gallons: Decimal
