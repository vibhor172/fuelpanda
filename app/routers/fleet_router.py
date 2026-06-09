from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.auth import get_current_admin
from app.dependencies.providers import get_fleet_handler
from app.handlers.fleet_handler import FleetHandler
from app.schemas.fleet import FleetStatusOut, VehicleLocation

router = APIRouter(prefix="/fleet", tags=["fleet"], dependencies=[Depends(get_current_admin)])


@router.get("/status", response_model=FleetStatusOut)
def fleet_status(handler: FleetHandler = Depends(get_fleet_handler)):
    return handler.status()


@router.get("/vehicles/{vehicle_id}/location", response_model=VehicleLocation)
def vehicle_location(vehicle_id: int, handler: FleetHandler = Depends(get_fleet_handler)):
    location = handler.vehicle_location(vehicle_id)
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No location recorded for this vehicle",
        )
    return location
