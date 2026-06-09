"""STUBBED auth — injects a fake identity. Real auth is out of scope per brief."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentUser:
    id: int
    role: str
    driver_id: int | None = None


def get_current_admin() -> CurrentUser:
    """Stub: every admin request runs as this fake admin."""
    return CurrentUser(id=1, role="admin")


def get_current_driver() -> CurrentUser:
    """Stub: every driver request runs as this fake driver (driver_id=1)."""
    return CurrentUser(id=2, role="driver", driver_id=1)
