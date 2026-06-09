from app.core.base_repository import BaseRepository
from app.models.location import Location


class LocationRepository(BaseRepository[Location]):
    model = Location
