from app.core.base_repository import BaseRepository
from app.models.driver import Driver


class DriverRepository(BaseRepository[Driver]):
    model = Driver
