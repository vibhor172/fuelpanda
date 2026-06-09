"""Application settings — Pydantic Settings as a Singleton via lru_cache."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://fleetpanda:fleetpanda@localhost:5432/fleetpanda"
    redis_url: str = "redis://localhost:6379/0"
    app_env: str = "local"
    log_level: str = "INFO"

    inventory_cache_ttl: int = 60
    alloc_lock_ttl: int = 10
    vehicle_location_ttl: int = 3600


@lru_cache
def get_settings() -> Settings:
    """Return the single Settings instance (Singleton)."""
    return Settings()
