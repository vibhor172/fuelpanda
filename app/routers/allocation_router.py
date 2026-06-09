from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_current_admin
from app.dependencies.providers import get_allocation_handler
from app.handlers.allocation_handler import AllocationHandler
from app.schemas.allocation import AllocationCreate, AllocationOut

router = APIRouter(
    prefix="/allocations", tags=["allocations"], dependencies=[Depends(get_current_admin)]
)


@router.post("", response_model=AllocationOut, status_code=status.HTTP_201_CREATED)
def create_allocation(
    payload: AllocationCreate, handler: AllocationHandler = Depends(get_allocation_handler)
):
    return handler.allocate(payload)


@router.get("", response_model=list[AllocationOut])
def list_allocations(
    allocation_date: date | None = Query(default=None),
    vehicle_id: int | None = Query(default=None),
    driver_id: int | None = Query(default=None),
    handler: AllocationHandler = Depends(get_allocation_handler),
):
    return handler.list(
        allocation_date=allocation_date, vehicle_id=vehicle_id, driver_id=driver_id
    )


@router.delete("/{allocation_id}", status_code=status.HTTP_204_NO_CONTENT)
def release_allocation(
    allocation_id: int, handler: AllocationHandler = Depends(get_allocation_handler)
):
    handler.release(allocation_id)
