from fastapi import APIRouter, Depends, status

from app.dependencies.auth import get_current_admin
from app.dependencies.providers import get_inventory_handler
from app.handlers.inventory_handler import InventoryHandler
from app.schemas.inventory import InventoryCreate, InventoryOut, InventoryUpdate

router = APIRouter(
    prefix="/inventory", tags=["inventory"], dependencies=[Depends(get_current_admin)]
)


@router.post("", response_model=InventoryOut, status_code=status.HTTP_201_CREATED)
def create_inventory(
    payload: InventoryCreate, handler: InventoryHandler = Depends(get_inventory_handler)
):
    return handler.create(payload)


@router.put("/{inventory_id}", response_model=InventoryOut)
def update_inventory(
    inventory_id: int,
    payload: InventoryUpdate,
    handler: InventoryHandler = Depends(get_inventory_handler),
):
    return handler.update(inventory_id, payload)


@router.get("")
def list_inventory(handler: InventoryHandler = Depends(get_inventory_handler)):
    """Monitor inventories across all locations (cached)."""
    return handler.list_all()
