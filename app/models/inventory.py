from sqlalchemy import CheckConstraint, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import BaseModel


class Inventory(BaseModel):
    __tablename__ = "inventories"

    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity_gallons: Mapped[float] = mapped_column(
        Numeric(14, 2), nullable=False, default=0
    )

    __table_args__ = (
        UniqueConstraint("location_id", "product_id", name="uq_inventory_location_product"),
        CheckConstraint("quantity_gallons >= 0", name="ck_inventory_non_negative"),
    )
