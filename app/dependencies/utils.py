"""Pure helpers: time, dates, pagination."""
from datetime import date, datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def today() -> date:
    return utcnow().date()


def paginate(limit: int | None, offset: int | None) -> tuple[int, int]:
    safe_limit = min(max(limit or 50, 1), 500)
    safe_offset = max(offset or 0, 0)
    return safe_limit, safe_offset
