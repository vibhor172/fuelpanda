"""Rule 1 — vehicle blocking via the partial unique index."""
from tests.integration.helpers import API, allocate, make_driver, make_vehicle


def test_allocation_creates_scheduled_shift_and_blocks_vehicle(client):
    v = make_vehicle(client)
    d = make_driver(client)
    r = allocate(client, v["id"], d["id"])
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "ACTIVE"

    veh = client.get(f"{API}/vehicles/{v['id']}").json()
    assert veh["status"] == "IN_USE"

    shifts = client.get(f"{API}/driver/shifts?scope=present").json()
    assert any(s["status"] == "SCHEDULED" for s in shifts)


def test_second_allocation_same_vehicle_same_day_conflicts(client):
    v = make_vehicle(client)
    d1 = make_driver(client, license_number="LIC-A")
    d2 = make_driver(client, license_number="LIC-B")

    first = allocate(client, v["id"], d1["id"])
    assert first.status_code == 201
    second = allocate(client, v["id"], d2["id"])
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "VEHICLE_ALREADY_ALLOCATED"


def test_release_frees_vehicle_for_reallocation_same_day(client):
    v = make_vehicle(client)
    d = make_driver(client)
    alloc = allocate(client, v["id"], d["id"]).json()

    rel = client.delete(f"{API}/allocations/{alloc['id']}")
    assert rel.status_code == 204

    veh = client.get(f"{API}/vehicles/{v['id']}").json()
    assert veh["status"] == "AVAILABLE"

    again = allocate(client, v["id"], d["id"])
    assert again.status_code == 201


def test_allocate_unknown_vehicle_404(client):
    d = make_driver(client)
    r = allocate(client, 999, d["id"])
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "VEHICLE_NOT_FOUND"
