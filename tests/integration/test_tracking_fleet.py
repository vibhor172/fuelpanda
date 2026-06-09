"""Rule 5 (GPS gating) + fleet-status read model (§13)."""
from tests.integration.helpers import API, allocate, make_driver, make_vehicle


def _started_shift(client):
    driver = make_driver(client)
    vehicle = make_vehicle(client)
    alloc = allocate(client, vehicle["id"], driver["id"]).json()
    shifts = client.get(f"{API}/driver/shifts?scope=present").json()
    shift = next(s for s in shifts if s["allocation_id"] == alloc["id"])
    client.post(f"{API}/driver/shifts/{shift['id']}/start")
    return shift, vehicle


def test_gps_rejected_without_active_shift(client):
    driver = make_driver(client)
    vehicle = make_vehicle(client)
    alloc = allocate(client, vehicle["id"], driver["id"]).json()
    shifts = client.get(f"{API}/driver/shifts?scope=present").json()
    shift = next(s for s in shifts if s["allocation_id"] == alloc["id"])
    r = client.post(
        f"{API}/driver/shifts/{shift['id']}/gps",
        json={"latitude": 1.0, "longitude": 2.0},
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "NO_ACTIVE_SHIFT_FOR_GPS"


def test_gps_ingest_appears_in_fleet_status(client):
    shift, vehicle = _started_shift(client)
    r = client.post(
        f"{API}/driver/shifts/{shift['id']}/gps",
        json={"latitude": 10.5, "longitude": 20.5},
    )
    assert r.status_code == 201

    status = client.get(f"{API}/fleet/status").json()
    assert status["source"] == "redis"
    assert status["count"] == 1
    assert status["vehicles"][0]["vehicle_id"] == vehicle["id"]
    assert status["vehicles"][0]["latitude"] == 10.5

    one = client.get(f"{API}/fleet/vehicles/{vehicle['id']}/location").json()
    assert one["longitude"] == 20.5


def test_fleet_status_cold_redis_falls_back_to_db(client, fake_redis):
    shift, vehicle = _started_shift(client)
    client.post(
        f"{API}/driver/shifts/{shift['id']}/gps",
        json={"latitude": 33.0, "longitude": 44.0},
    )
    fake_redis.flushall()

    status = client.get(f"{API}/fleet/status").json()
    assert status["source"] == "db"
    assert status["count"] == 1
    assert status["vehicles"][0]["latitude"] == 33.0


def test_gps_history_returns_points(client):
    shift, vehicle = _started_shift(client)
    for lng in (1.0, 2.0, 3.0):
        client.post(
            f"{API}/driver/shifts/{shift['id']}/gps",
            json={"latitude": 5.0, "longitude": lng},
        )
    hist = client.get(f"{API}/tracking/vehicles/{vehicle['id']}/history").json()
    assert len(hist) == 3
