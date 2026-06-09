from fastapi import APIRouter, Depends

from app.dependencies.auth import CurrentUser, get_current_driver
from app.dependencies.constants import ShiftScope
from app.dependencies.providers import get_shift_handler
from app.handlers.shift_handler import ShiftHandler
from app.schemas.shift import ShiftDetailOut, ShiftOut, ShiftVehicleOut

router = APIRouter(prefix="/driver/shifts", tags=["shifts"])


def _detail(shift, vehicle) -> ShiftDetailOut:
    out = ShiftDetailOut.model_validate(shift)
    out.vehicle = ShiftVehicleOut.model_validate(vehicle) if vehicle else None
    return out


@router.get("", response_model=list[ShiftDetailOut])
def list_shifts(
    scope: ShiftScope = ShiftScope.PRESENT,
    user: CurrentUser = Depends(get_current_driver),
    handler: ShiftHandler = Depends(get_shift_handler),
):
    shifts = handler.list_for_driver(user.driver_id, scope)
    return [_detail(s, handler.vehicle_for(s)) for s in shifts]


@router.get("/{shift_id}", response_model=ShiftDetailOut)
def get_shift(
    shift_id: int,
    _: CurrentUser = Depends(get_current_driver),
    handler: ShiftHandler = Depends(get_shift_handler),
):
    shift = handler.get(shift_id)
    return _detail(shift, handler.vehicle_for(shift))


@router.post("/{shift_id}/start", response_model=ShiftOut)
def start_shift(
    shift_id: int,
    _: CurrentUser = Depends(get_current_driver),
    handler: ShiftHandler = Depends(get_shift_handler),
):
    return handler.start(shift_id)


@router.post("/{shift_id}/end", response_model=ShiftOut)
def end_shift(
    shift_id: int,
    _: CurrentUser = Depends(get_current_driver),
    handler: ShiftHandler = Depends(get_shift_handler),
):
    return handler.end(shift_id)
