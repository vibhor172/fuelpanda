"""Shift handler transitions with mocked repositories (Rule 3)."""
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.custom_exceptions.shift_exceptions import (
    InvalidShiftTransition,
    NoAllocationForShift,
    ShiftNotActive,
)
from app.dependencies.constants import ShiftStatus
from app.handlers.shift_handler import ShiftHandler


def _handler(shift, active_allocation=None, open_orders=None):
    repo = MagicMock()
    repo.get.return_value = shift
    allocation_repo = MagicMock()
    allocation_repo.get_active_for_driver_date.return_value = active_allocation
    allocation_repo.get.return_value = SimpleNamespace(
        id=1, vehicle_id=1, allocation_date=date(2026, 6, 7)
    )
    order_repo = MagicMock()
    order_repo.list_open_for_shift.return_value = open_orders or []
    vehicle_repo = MagicMock()
    vehicle_repo.get.return_value = SimpleNamespace(id=1, status="IN_USE")
    return ShiftHandler(MagicMock(), repo, allocation_repo, order_repo, vehicle_repo, MagicMock())


def _shift(status=ShiftStatus.SCHEDULED):
    return SimpleNamespace(
        id=1, driver_id=1, allocation_id=1, shift_date=date(2026, 6, 7),
        status=status, started_at=None, ended_at=None,
    )


def test_start_requires_active_allocation():
    handler = _handler(_shift(), active_allocation=None)
    with pytest.raises(NoAllocationForShift):
        handler.start(1)


def test_start_rejects_non_scheduled_shift():
    handler = _handler(_shift(status=ShiftStatus.ACTIVE))
    with pytest.raises(InvalidShiftTransition):
        handler.start(1)


def test_start_activates_shift_with_allocation():
    handler = _handler(_shift(), active_allocation=SimpleNamespace(id=1))
    result = handler.start(1)
    assert result.status == ShiftStatus.ACTIVE
    assert result.started_at is not None


def test_end_requires_active_shift():
    handler = _handler(_shift(status=ShiftStatus.SCHEDULED))
    with pytest.raises(ShiftNotActive):
        handler.end(1)


def test_end_auto_fails_open_orders():
    open_order = SimpleNamespace(status=None, failure_reason=None)
    handler = _handler(_shift(status=ShiftStatus.ACTIVE), open_orders=[open_order])
    handler.end(1)
    assert open_order.status == "FAILED"
    assert open_order.failure_reason == "UNCOMPLETED_AT_SHIFT_END"
