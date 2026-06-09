"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-07
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _ts(table: sa.Table | None = None) -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    location_type = sa.Enum("HUB", "TERMINAL", name="location_type")
    driver_status = sa.Enum("ACTIVE", "INACTIVE", name="driver_status")
    vehicle_status = sa.Enum("AVAILABLE", "IN_USE", "MAINTENANCE", name="vehicle_status")
    allocation_status = sa.Enum("ACTIVE", "RELEASED", name="allocation_status")
    shift_status = sa.Enum("SCHEDULED", "ACTIVE", "COMPLETED", name="shift_status")
    order_status = sa.Enum("PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", name="order_status")

    op.create_table(
        "locations",
        *_ts(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", location_type, nullable=False),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=True),
    )
    op.create_index("ix_locations_type", "locations", ["type"])

    op.create_table(
        "products",
        *_ts(),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("unit", sa.String(32), nullable=False, server_default="gallons"),
    )

    op.create_table(
        "inventories",
        *_ts(),
        sa.Column("location_id", sa.Integer, sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity_gallons", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.UniqueConstraint("location_id", "product_id", name="uq_inventory_location_product"),
        sa.CheckConstraint("quantity_gallons >= 0", name="ck_inventory_non_negative"),
    )

    op.create_table(
        "drivers",
        *_ts(),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("license_number", sa.String(64), nullable=False, unique=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("status", driver_status, nullable=False, server_default="ACTIVE"),
    )

    op.create_table(
        "vehicles",
        *_ts(),
        sa.Column("registration_number", sa.String(64), nullable=False, unique=True),
        sa.Column("capacity_gallons", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", vehicle_status, nullable=False, server_default="AVAILABLE"),
        sa.Column("last_latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("last_longitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "vehicle_allocations",
        *_ts(),
        sa.Column("vehicle_id", sa.Integer, sa.ForeignKey("vehicles.id"), nullable=False),
        sa.Column("driver_id", sa.Integer, sa.ForeignKey("drivers.id"), nullable=False),
        sa.Column("allocation_date", sa.Date, nullable=False),
        sa.Column("status", allocation_status, nullable=False, server_default="ACTIVE"),
    )
    op.create_index(
        "uq_alloc_vehicle_date_active",
        "vehicle_allocations",
        ["vehicle_id", "allocation_date"],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )
    op.create_index(
        "uq_alloc_driver_date_active",
        "vehicle_allocations",
        ["driver_id", "allocation_date"],
        unique=True,
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )

    op.create_table(
        "shifts",
        *_ts(),
        sa.Column("driver_id", sa.Integer, sa.ForeignKey("drivers.id"), nullable=False),
        sa.Column("allocation_id", sa.Integer, sa.ForeignKey("vehicle_allocations.id"), nullable=False),
        sa.Column("shift_date", sa.Date, nullable=False),
        sa.Column("status", shift_status, nullable=False, server_default="SCHEDULED"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("driver_id", "shift_date", name="uq_shift_driver_date"),
    )

    op.create_table(
        "orders",
        *_ts(),
        sa.Column("shift_id", sa.Integer, sa.ForeignKey("shifts.id"), nullable=False),
        sa.Column("destination_id", sa.Integer, sa.ForeignKey("locations.id"), nullable=False),
        sa.Column("status", order_status, nullable=False, server_default="PENDING"),
        sa.Column("failure_reason", sa.Text, nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_orders_shift_id", "orders", ["shift_id"])
    op.create_index("ix_orders_status", "orders", ["status"])

    op.create_table(
        "order_items",
        *_ts(),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity_gallons", sa.Numeric(14, 2), nullable=False),
        sa.UniqueConstraint("order_id", "product_id", name="uq_order_item_order_product"),
        sa.CheckConstraint("quantity_gallons > 0", name="ck_order_item_positive"),
    )

    op.create_table(
        "gps_locations",
        *_ts(),
        sa.Column("vehicle_id", sa.Integer, sa.ForeignKey("vehicles.id"), nullable=False),
        sa.Column("shift_id", sa.Integer, sa.ForeignKey("shifts.id"), nullable=False),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_gps_vehicle_recorded", "gps_locations", ["vehicle_id", "recorded_at"])
    op.create_index("ix_gps_shift_recorded", "gps_locations", ["shift_id", "recorded_at"])


def downgrade() -> None:
    op.drop_table("gps_locations")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("shifts")
    op.drop_index("uq_alloc_driver_date_active", table_name="vehicle_allocations")
    op.drop_index("uq_alloc_vehicle_date_active", table_name="vehicle_allocations")
    op.drop_table("vehicle_allocations")
    op.drop_table("vehicles")
    op.drop_table("drivers")
    op.drop_table("inventories")
    op.drop_table("products")
    op.drop_index("ix_locations_type", table_name="locations")
    op.drop_table("locations")
    for name in (
        "order_status",
        "shift_status",
        "allocation_status",
        "vehicle_status",
        "driver_status",
        "location_type",
    ):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
