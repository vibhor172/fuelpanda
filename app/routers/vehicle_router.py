from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_current_admin
from app.dependencies.providers import get_vehicle_handler
from app.handlers.vehicle_handler import VehicleHandler
from app.schemas.vehicle import VehicleCreate, VehicleOut, VehicleUpdate

router = APIRouter(
    prefix="/vehicles", tags=["vehicles"], dependencies=[Depends(get_current_admin)]
)


@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate, handler: VehicleHandler = Depends(get_vehicle_handler)):
    return handler.create(payload)


@router.put("/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(
    vehicle_id: int,
    payload: VehicleUpdate,
    handler: VehicleHandler = Depends(get_vehicle_handler),
):
    return handler.update(vehicle_id, payload)


@router.get("", response_model=list[VehicleOut])
def list_vehicles(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    handler: VehicleHandler = Depends(get_vehicle_handler),
):
    return handler.list(limit=limit, offset=offset)


@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: int, handler: VehicleHandler = Depends(get_vehicle_handler)):
    return handler.get(vehicle_id)
