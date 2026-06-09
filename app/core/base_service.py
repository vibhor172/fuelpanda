"""Service base — wraps the Redis client for cross-cutting concerns."""
import redis


class BaseService:
    def __init__(self, redis_client: redis.Redis) -> None:
        self.redis = redis_client
