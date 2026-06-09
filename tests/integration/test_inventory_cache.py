"""Inventory monitoring cache: served from cache, invalidated on write (§12)."""
from app.dependencies.constants import CacheKeys
from tests.integration.helpers import API, make_location, make_product


def test_inventory_all_is_cached_and_invalidated(client, fake_redis):
    loc = make_location(client)
    product = make_product(client)
    client.post(
        f"{API}/inventory",
        json={"location_id": loc["id"], "product_id": product["id"], "quantity_gallons": 10},
    )

    first = client.get(f"{API}/inventory").json()
    assert len(first) == 1
    assert fake_redis.get(CacheKeys.INVENTORY_ALL) is not None

    loc2 = make_location(client, name="Hub 2")
    client.post(
        f"{API}/inventory",
        json={"location_id": loc2["id"], "product_id": product["id"], "quantity_gallons": 5},
    )
    assert fake_redis.get(CacheKeys.INVENTORY_ALL) is None

    second = client.get(f"{API}/inventory").json()
    assert len(second) == 2
