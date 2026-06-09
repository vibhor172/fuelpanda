"""CRUD + validation/error envelope for master-data modules."""
from tests.integration.helpers import API, make_driver, make_location, make_product


def test_location_crud(client):
    loc = make_location(client)
    assert loc["type"] == "HUB"

    got = client.get(f"{API}/locations/{loc['id']}")
    assert got.status_code == 200

    upd = client.put(f"{API}/locations/{loc['id']}", json={"name": "Hub B"})
    assert upd.json()["name"] == "Hub B"

    listed = client.get(f"{API}/locations")
    assert len(listed.json()) == 1


def test_location_not_found_envelope(client):
    r = client.get(f"{API}/locations/999")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "LOCATION_NOT_FOUND"


def test_duplicate_product_conflict(client):
    make_product(client, name="Diesel", code="DIESEL")
    r = client.post(f"{API}/products", json={"name": "Diesel", "code": "DIESEL"})
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "DUPLICATE_PRODUCT"


def test_duplicate_driver_license_conflict(client):
    make_driver(client, license_number="LIC-9")
    r = client.post(
        f"{API}/drivers", json={"name": "Other", "license_number": "LIC-9"}
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "DUPLICATE_DRIVER_LICENSE"


def test_validation_error_envelope(client):
    r = client.post(f"{API}/vehicles", json={"registration_number": "R", "capacity_gallons": -1})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"
