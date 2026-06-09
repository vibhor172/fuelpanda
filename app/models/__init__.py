"""Import all models so Alembic/metadata sees every table."""
from app.models.driver import Driver
from app.models.gps_location import GpsLocation
from app.models.inventory import Inventory
from app.models.location import Location
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.shift import Shift
from app.models.vehicle import Vehicle
from app.models.vehicle_allocation import VehicleAllocation

__all__ = [
    "Driver",
    "GpsLocation",
    "Inventory",
    "Location",
    "Order",
    "OrderItem",
    "Product",
    "Shift",
    "Vehicle",
    "VehicleAllocation",
]
