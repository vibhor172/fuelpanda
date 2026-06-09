from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import BaseModel
from app.dependencies.constants import OrderStatus


class Order(BaseModel):
    __tablename__ = "orders"

    shift_id: Mapped[int] = mapped_column(ForeignKey("shifts.id"), nullable=False)
    destination_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        nullable=False,
        default=OrderStatus.PENDING,
    )
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    shift = relationship("Shift", back_populates="orders")
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_orders_shift_id", "shift_id"),
        Index("ix_orders_status", "status"),
    )


class OrderItem(BaseModel):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity_gallons: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    order = relationship("Order", back_populates="items")

    __table_args__ = (
        UniqueConstraint("order_id", "product_id", name="uq_order_item_order_product"),
        CheckConstraint("quantity_gallons > 0", name="ck_order_item_positive"),
    )
