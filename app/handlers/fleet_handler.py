"""Fleet read model (context.md §13). Read-only — no repo of its own."""
from app.core.base_handler import BaseHandler
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.fleet import FleetStatusOut, VehicleLocation
from app.services.fleet_status_service import FleetStatusService


class FleetHandler(BaseHandler):
    def __init__(
        self, db, vehicle_repo: VehicleRepository, fleet_service: FleetStatusService
    ) -> None:
        super().__init__(db)
        self.vehicle_repo = vehicle_repo
        self.fleet_service = fleet_service

    def status(self) -> FleetStatusOut:
        return self.fleet_service.get_status(self.vehicle_repo)

    def vehicle_location(self, vehicle_id: int) -> VehicleLocation | None:
        return self.fleet_service.get_vehicle_location(vehicle_id, self.vehicle_repo)
