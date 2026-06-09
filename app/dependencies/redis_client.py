"""Redis connection pool (Singleton) and get_redis() dependency."""
from functools import lru_cache

import redis

from app.dependencies.config import get_settings


@lru_cache
def _get_pool() -> redis.ConnectionPool:
    settings = get_settings()
    return redis.ConnectionPool.from_url(settings.redis_url, decode_responses=True)


def get_redis() -> redis.Redis:
    """Return a Redis client backed by the shared pool."""
    return redis.Redis(connection_pool=_get_pool())
