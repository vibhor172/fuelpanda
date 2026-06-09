from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_current_admin
from app.dependencies.providers import get_driver_handler
from app.handlers.driver_handler import DriverHandler
from app.schemas.driver import DriverCreate, DriverOut, DriverUpdate

router = APIRouter(
    prefix="/drivers", tags=["drivers"], dependencies=[Depends(get_current_admin)]
)


@router.post("", response_model=DriverOut, status_code=status.HTTP_201_CREATED)
def create_driver(payload: DriverCreate, handler: DriverHandler = Depends(get_driver_handler)):
    return handler.create(payload)


@router.put("/{driver_id}", response_model=DriverOut)
def update_driver(
    driver_id: int, payload: DriverUpdate, handler: DriverHandler = Depends(get_driver_handler)
):
    return handler.update(driver_id, payload)


@router.get("", response_model=list[DriverOut])
def list_drivers(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    handler: DriverHandler = Depends(get_driver_handler),
):
    return handler.list(limit=limit, offset=offset)


@router.get("/{driver_id}", response_model=DriverOut)
def get_driver(driver_id: int, handler: DriverHandler = Depends(get_driver_handler)):
    return handler.get(driver_id)
