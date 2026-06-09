import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.custom_exceptions.base_exception import AppException
from app.routers import (
    allocation_router,
    driver_router,
    fleet_router,
    inventory_router,
    location_router,
    order_router,
    product_router,
    shift_router,
    tracking_router,
    vehicle_router,
)

logger = logging.getLogger("fleetpanda")

app = FastAPI(title="FuelPanda — Fleet Tracking Platform", version="0.1.0")

API_PREFIX = "/api/v1"

for module in (
    location_router,
    product_router,
    inventory_router,
    driver_router,
    vehicle_router,
    allocation_router,
    fleet_router,
):
    app.include_router(module.router, prefix=API_PREFIX)

app.include_router(order_router.router, prefix=API_PREFIX)
app.include_router(order_router.driver_router, prefix=API_PREFIX)

app.include_router(shift_router.router, prefix=API_PREFIX)
app.include_router(tracking_router.gps_router, prefix=API_PREFIX)
app.include_router(tracking_router.history_router, prefix=API_PREFIX)


@app.exception_handler(AppException)
async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(status_code=exc.http_status, content=exc.to_dict())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": jsonable_encoder(exc.errors()),
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}},
    )


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
