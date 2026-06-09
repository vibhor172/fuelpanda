from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_current_admin, get_current_driver
from app.dependencies.providers import get_tracking_handler
from app.dependencies.utils import paginate
from app.handlers.tracking_handler import TrackingHandler
from app.schemas.tracking import GpsIn, GpsOut

gps_router = APIRouter(
    prefix="/driver/shifts", tags=["tracking"], dependencies=[Depends(get_current_driver)]
)


@gps_router.post("/{shift_id}/gps", response_model=GpsOut, status_code=status.HTTP_201_CREATED)
def ingest_gps(
    shift_id: int, payload: GpsIn, handler: TrackingHandler = Depends(get_tracking_handler)
):
    return handler.ingest(shift_id, payload)


history_router = APIRouter(
    prefix="/tracking", tags=["tracking"], dependencies=[Depends(get_current_admin)]
)


@history_router.get("/vehicles/{vehicle_id}/history", response_model=list[GpsOut])
def vehicle_history(
    vehicle_id: int,
    from_ts: datetime | None = Query(default=None, alias="from"),
    to_ts: datetime | None = Query(default=None, alias="to"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    handler: TrackingHandler = Depends(get_tracking_handler),
):
    safe_limit, safe_offset = paginate(limit, offset)
    return handler.history(
        vehicle_id, from_ts=from_ts, to_ts=to_ts, limit=safe_limit, offset=safe_offset
    )
