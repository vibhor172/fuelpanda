"""Order handler business logic with mocked repositories (Rule 2)."""
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.custom_exceptions.order_exceptions import (
    DeliveryAlreadyFinalized,
    MissingFailureReason,
)
from app.dependencies.constants import OrderStatus, ShiftStatus
from app.handlers.order_handler import OrderHandler


def _order(status=OrderStatus.PENDING, items=None):
    return SimpleNamespace(
        id=1,
        shift_id=1,
        destination_id=10,
        status=status,
        failure_reason=None,
        completed_at=None,
        items=items or [],
    )


def _make_handler(order, inventory):
    repo = MagicMock()
    repo.get_for_update.return_value = order
    shift_repo = MagicMock()
    shift_repo.get.return_value = SimpleNamespace(id=1, status=ShiftStatus.ACTIVE)
    inventory_repo = MagicMock()
    inventory_repo.get_locked.return_value = inventory
    cache = MagicMock()
    handler = OrderHandler(
        db=MagicMock(),
        repo=repo,
        shift_repo=shift_repo,
        location_repo=MagicMock(),
        product_repo=MagicMock(),
        inventory_repo=inventory_repo,
        cache=cache,
    )
    return handler


def test_complete_bumps_inventory_and_marks_completed():
    item = SimpleNamespace(product_id=2, quantity_gallons=Decimal("100"))
    inv = SimpleNamespace(quantity_gallons=Decimal("50"))
    handler = _make_handler(_order(items=[item]), inv)

    result = handler.complete(1)

    assert inv.quantity_gallons == Decimal("150")
    assert result.status == OrderStatus.COMPLETED
    assert result.completed_at is not None
    handler.cache.invalidate_inventory.assert_called_once_with(10)


def test_complete_is_idempotent_after_finalized():
    handler = _make_handler(_order(status=OrderStatus.COMPLETED), None)
    with pytest.raises(DeliveryAlreadyFinalized):
        handler.complete(1)


def test_fail_sets_reason_and_does_not_touch_inventory():
    handler = _make_handler(_order(), None)
    result = handler.fail(1, "tank empty")
    assert result.status == OrderStatus.FAILED
    assert result.failure_reason == "tank empty"
    handler.inventory_repo.get_locked.assert_not_called()


def test_fail_requires_reason():
    handler = _make_handler(_order(), None)
    with pytest.raises(MissingFailureReason):
        handler.fail(1, "   ")
