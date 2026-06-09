from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_current_admin
from app.handlers.inventory_handler import InventoryHandler
from app.handlers.location_handler import LocationHandler
from app.dependencies.providers import get_inventory_handler, get_location_handler
from app.schemas.location import LocationCreate, LocationOut, LocationUpdate

router = APIRouter(
    prefix="/locations", tags=["locations"], dependencies=[Depends(get_current_admin)]
)


@router.post("", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(
    payload: LocationCreate, handler: LocationHandler = Depends(get_location_handler)
):
    return handler.create(payload)


@router.put("/{location_id}", response_model=LocationOut)
def update_location(
    location_id: int,
    payload: LocationUpdate,
    handler: LocationHandler = Depends(get_location_handler),
):
    return handler.update(location_id, payload)


@router.get("", response_model=list[LocationOut])
def list_locations(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    handler: LocationHandler = Depends(get_location_handler),
):
    return handler.list(limit=limit, offset=offset)


@router.get("/{location_id}", response_model=LocationOut)
def get_location(location_id: int, handler: LocationHandler = Depends(get_location_handler)):
    return handler.get(location_id)


@router.get("/{location_id}/inventory")
def location_inventory(
    location_id: int, handler: InventoryHandler = Depends(get_inventory_handler)
):
    return handler.list_for_location(location_id)
