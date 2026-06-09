from sqlalchemy.exc import IntegrityError

from app.core.base_handler import BaseHandler
from app.custom_exceptions.vehicle_exceptions import (
    DuplicateVehicleRegistration,
    VehicleNotFound,
)
from app.models.vehicle import Vehicle
from app.repositories.vehicle_repository import VehicleRepository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleHandler(BaseHandler):
    def __init__(self, db, repo: VehicleRepository) -> None:
        super().__init__(db)
        self.repo = repo

    def create(self, data: VehicleCreate) -> Vehicle:
        vehicle = Vehicle(**data.model_dump())
        try:
            self.repo.create(vehicle)
            self.commit()
        except IntegrityError:
            self.rollback()
            raise DuplicateVehicleRegistration(
                details={"registration_number": data.registration_number}
            ) from None
        return vehicle

    def update(self, vehicle_id: int, data: VehicleUpdate) -> Vehicle:
        vehicle = self._get(vehicle_id)
        self.repo.update(vehicle, data.model_dump(exclude_unset=True))
        self.commit()
        return vehicle

    def get(self, vehicle_id: int) -> Vehicle:
        return self._get(vehicle_id)

    def list(self, *, limit: int, offset: int) -> list[Vehicle]:
        return self.repo.list(limit=limit, offset=offset)

    def _get(self, vehicle_id: int) -> Vehicle:
        vehicle = self.repo.get(vehicle_id)
        if vehicle is None:
            raise VehicleNotFound(details={"id": vehicle_id})
        return vehicle
