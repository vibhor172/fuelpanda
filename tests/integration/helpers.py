"""Small builders for seeding master data through the HTTP API."""
from app.dependencies.utils import today

API = "/api/v1"


def make_location(client, name="Hub A", type_="HUB"):
    r = client.post(f"{API}/locations", json={"name": name, "type": type_})
    assert r.status_code == 201, r.text
    return r.json()


def make_product(client, name="Diesel", code="DIESEL"):
    r = client.post(f"{API}/products", json={"name": name, "code": code})
    assert r.status_code == 201, r.text
    return r.json()


def make_driver(client, name="Sam", license_number="LIC-1"):
    r = client.post(
        f"{API}/drivers", json={"name": name, "license_number": license_number}
    )
    assert r.status_code == 201, r.text
    return r.json()


def make_vehicle(client, registration_number="REG-1", capacity=1000):
    r = client.post(
        f"{API}/vehicles",
        json={"registration_number": registration_number, "capacity_gallons": capacity},
    )
    assert r.status_code == 201, r.text
    return r.json()


def allocate(client, vehicle_id, driver_id, on=None):
    on = on or today()
    return client.post(
        f"{API}/allocations",
        json={
            "vehicle_id": vehicle_id,
            "driver_id": driver_id,
            "allocation_date": on.isoformat(),
        },
    )
