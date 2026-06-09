"""Redis distributed lock (SET NX EX) — defense-in-depth only.

Correctness never depends on this lock; the DB unique constraint is authoritative
(context.md §11 Rule 4). The lock just reduces contention / gives early rejection.
"""
from contextlib import contextmanager
from collections.abc import Iterator

from app.core.base_service import BaseService


class LockService(BaseService):
    @contextmanager
    def acquire(self, key: str, ttl: int) -> Iterator[bool]:
        """Best-effort lock. Yields True if acquired, False otherwise.

        Never blocks the caller — a False result simply means another worker holds it.
        """
        acquired = bool(self.redis.set(key, "1", nx=True, ex=ttl))
        try:
            yield acquired
        finally:
            if acquired:
                self.redis.delete(key)
