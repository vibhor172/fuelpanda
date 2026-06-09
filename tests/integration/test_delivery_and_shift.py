"""Rule 2 (inventory consistency) + Rule 3 (shift lifecycle)."""
from tests.integration.helpers import (
    API,
    allocate,
    make_driver,
    make_location,
    make_product,
    make_vehicle,
)


def _active_shift(client):
    """Seed master data, allocate, and start a shift. Returns (shift, dest, product)."""
    dest = make_location(client, name="Terminal X", type_="TERMINAL")
    product = make_product(client)
    driver = make_driver(client)
    vehicle = make_vehicle(client)
    alloc = allocate(client, vehicle["id"], driver["id"]).json()
    shifts = client.get(f"{API}/driver/shifts?scope=present").json()
    shift = next(s for s in shifts if s["allocation_id"] == alloc["id"])
    started = client.post(f"{API}/driver/shifts/{shift['id']}/start")
    assert started.status_code == 200, started.text
    assert started.json()["status"] == "ACTIVE"
    return shift, dest, product, vehicle


def _order(client, shift_id, dest_id, product_id, qty):
    r = client.post(
        f"{API}/orders",
        json={
            "shift_id": shift_id,
            "destination_id": dest_id,
            "items": [{"product_id": product_id, "quantity_gallons": qty}],
        },
    )
    assert r.status_code == 201, r.text
    return r.json()


def test_complete_delivery_adds_to_inventory(client):
    shift, dest, product, _ = _active_shift(client)
    client.post(
        f"{API}/inventory",
        json={"location_id": dest["id"], "product_id": product["id"], "quantity_gallons": 50},
    )
    order = _order(client, shift["id"], dest["id"], product["id"], 100)

    done = client.post(f"{API}/driver/orders/{order['id']}/complete")
    assert done.status_code == 200
    assert done.json()["status"] == "COMPLETED"

    inv = client.get(f"{API}/locations/{dest['id']}/inventory").json()
    qty = float(next(i["quantity_gallons"] for i in inv if i["product_id"] == product["id"]))
    assert qty == 150.0


def test_complete_creates_inventory_when_absent(client):
    shift, dest, product, _ = _active_shift(client)
    order = _order(client, shift["id"], dest["id"], product["id"], 75)
    client.post(f"{API}/driver/orders/{order['id']}/complete")
    inv = client.get(f"{API}/locations/{dest['id']}/inventory").json()
    assert float(inv[0]["quantity_gallons"]) == 75.0


def test_double_complete_is_rejected(client):
    shift, dest, product, _ = _active_shift(client)
    order = _order(client, shift["id"], dest["id"], product["id"], 10)
    assert client.post(f"{API}/driver/orders/{order['id']}/complete").status_code == 200
    again = client.post(f"{API}/driver/orders/{order['id']}/complete")
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "DELIVERY_ALREADY_FINALIZED"


def test_fail_delivery_requires_reason_and_skips_inventory(client):
    shift, dest, product, _ = _active_shift(client)
    client.post(
        f"{API}/inventory",
        json={"location_id": dest["id"], "product_id": product["id"], "quantity_gallons": 40},
    )
    order = _order(client, shift["id"], dest["id"], product["id"], 100)

    missing = client.post(f"{API}/driver/orders/{order['id']}/fail", json={"reason": ""})
    assert missing.status_code == 422

    failed = client.post(
        f"{API}/driver/orders/{order['id']}/fail", json={"reason": "no access"}
    )
    assert failed.status_code == 200
    assert failed.json()["status"] == "FAILED"

    inv = client.get(f"{API}/locations/{dest['id']}/inventory").json()
    assert float(inv[0]["quantity_gallons"]) == 40.0


def test_shift_end_auto_fails_open_orders_and_frees_vehicle(client):
    shift, dest, product, vehicle = _active_shift(client)
    order = _order(client, shift["id"], dest["id"], product["id"], 20)

    ended = client.post(f"{API}/driver/shifts/{shift['id']}/end")
    assert ended.status_code == 200
    assert ended.json()["status"] == "COMPLETED"

    got = client.get(f"{API}/orders/{order['id']}").json()
    assert got["status"] == "FAILED"
    assert got["failure_reason"] == "UNCOMPLETED_AT_SHIFT_END"

    veh = client.get(f"{API}/vehicles/{vehicle['id']}").json()
    assert veh["status"] == "AVAILABLE"


def test_release_removes_scheduled_shift(client):
    driver = make_driver(client)
    vehicle = make_vehicle(client)
    alloc = allocate(client, vehicle["id"], driver["id"]).json()
    shifts = client.get(f"{API}/driver/shifts?scope=present").json()
    shift = next(s for s in shifts if s["allocation_id"] == alloc["id"])

    client.delete(f"{API}/allocations/{alloc['id']}")
    started = client.post(f"{API}/driver/shifts/{shift['id']}/start")
    assert started.status_code == 404
    assert started.json()["error"]["code"] == "SHIFT_NOT_FOUND"
