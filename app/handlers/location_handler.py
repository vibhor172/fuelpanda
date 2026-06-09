from app.core.base_handler import BaseHandler
from app.custom_exceptions.location_exceptions import LocationNotFound
from app.models.location import Location
from app.repositories.location_repository import LocationRepository
from app.schemas.location import LocationCreate, LocationUpdate


class LocationHandler(BaseHandler):
    def __init__(self, db, repo: LocationRepository) -> None:
        super().__init__(db)
        self.repo = repo

    def create(self, data: LocationCreate) -> Location:
        location = Location(**data.model_dump())
        self.repo.create(location)
        self.commit()
        return location

    def update(self, location_id: int, data: LocationUpdate) -> Location:
        location = self._get(location_id)
        self.repo.update(location, data.model_dump(exclude_unset=True))
        self.commit()
        return location

    def get(self, location_id: int) -> Location:
        return self._get(location_id)

    def list(self, *, limit: int, offset: int) -> list[Location]:
        return self.repo.list(limit=limit, offset=offset)

    def _get(self, location_id: int) -> Location:
        location = self.repo.get(location_id)
        if location is None:
            raise LocationNotFound(details={"id": location_id})
        return location
