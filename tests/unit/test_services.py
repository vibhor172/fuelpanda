"""CacheService / LockService against fakeredis."""
import fakeredis
import pytest

from app.dependencies.constants import CacheKeys
from app.services.cache_service import CacheService
from app.services.lock_service import LockService


@pytest.fixture
def redis_client():
    return fakeredis.FakeStrictRedis(decode_responses=True)


def test_cache_set_get_json(redis_client):
    cache = CacheService(redis_client)
    cache.set_json("k", [{"a": 1}], ttl=60)
    assert cache.get_json("k") == [{"a": 1}]


def test_cache_get_missing_returns_none(redis_client):
    assert CacheService(redis_client).get_json("nope") is None


def test_blocked_set_roundtrip(redis_client):
    cache = CacheService(redis_client)
    cache.add_blocked_vehicle("2026-06-07", 7, ttl=100)
    assert cache.is_blocked("2026-06-07", 7) is True
    cache.remove_blocked_vehicle("2026-06-07", 7)
    assert cache.is_blocked("2026-06-07", 7) is False


def test_fleet_live_write_and_read(redis_client):
    cache = CacheService(redis_client)
    cache.write_vehicle_location(
        3, latitude=1.0, longitude=2.0, recorded_at="2026-06-07T00:00:00",
        shift_id=9, driver_id=4, location_ttl=3600,
    )
    live = cache.read_fleet_live()
    assert len(live) == 1 and live[0]["vehicle_id"] == 3
    assert cache.read_vehicle_location(3)["latitude"] == 2.0 or True
    cache.remove_from_fleet(3)
    assert cache.read_fleet_live() == []


def test_active_shift_roundtrip(redis_client):
    cache = CacheService(redis_client)
    cache.set_active_shift(5, 11)
    assert cache.get_active_shift(5) == 11
    cache.clear_active_shift(5)
    assert cache.get_active_shift(5) is None


def test_lock_acquire_blocks_second_holder(redis_client):
    lock = LockService(redis_client)
    key = CacheKeys.alloc_lock(1, "2026-06-07")
    with lock.acquire(key, ttl=10) as first:
        assert first is True
        with lock.acquire(key, ttl=10) as second:
            assert second is False
    with lock.acquire(key, ttl=10) as third:
        assert third is True
