"""Pydantic request-schema validation (the framework's first line of defense)."""
import pytest
from pydantic import ValidationError

from app.schemas.inventory import InventoryCreate
from app.schemas.order import OrderCreate, OrderFail, OrderItemIn
from app.schemas.tracking import GpsIn


def test_gps_rejects_out_of_range_latitude():
    with pytest.raises(ValidationError):
        GpsIn(latitude=91, longitude=0)


def test_gps_rejects_out_of_range_longitude():
    with pytest.raises(ValidationError):
        GpsIn(latitude=0, longitude=-181)


def test_gps_accepts_valid_coordinates():
    gps = GpsIn(latitude=12.34, longitude=56.78)
    assert float(gps.latitude) == 12.34


def test_order_item_rejects_non_positive_quantity():
    with pytest.raises(ValidationError):
        OrderItemIn(product_id=1, quantity_gallons=0)


def test_order_requires_at_least_one_item():
    with pytest.raises(ValidationError):
        OrderCreate(shift_id=1, destination_id=1, items=[])


def test_fail_reason_must_be_non_empty():
    with pytest.raises(ValidationError):
        OrderFail(reason="")


def test_inventory_rejects_negative_quantity():
    with pytest.raises(ValidationError):
        InventoryCreate(location_id=1, product_id=1, quantity_gallons=-5)
