from sqlalchemy.exc import IntegrityError

from app.core.base_handler import BaseHandler
from app.custom_exceptions.driver_exceptions import DriverNotFound, DuplicateDriverLicense
from app.models.driver import Driver
from app.repositories.driver_repository import DriverRepository
from app.schemas.driver import DriverCreate, DriverUpdate


class DriverHandler(BaseHandler):
    def __init__(self, db, repo: DriverRepository) -> None:
        super().__init__(db)
        self.repo = repo

    def create(self, data: DriverCreate) -> Driver:
        driver = Driver(**data.model_dump())
        try:
            self.repo.create(driver)
            self.commit()
        except IntegrityError:
            self.rollback()
            raise DuplicateDriverLicense(
                details={"license_number": data.license_number}
            ) from None
        return driver

    def update(self, driver_id: int, data: DriverUpdate) -> Driver:
        driver = self._get(driver_id)
        self.repo.update(driver, data.model_dump(exclude_unset=True))
        self.commit()
        return driver

    def get(self, driver_id: int) -> Driver:
        return self._get(driver_id)

    def list(self, *, limit: int, offset: int) -> list[Driver]:
        return self.repo.list(limit=limit, offset=offset)

    def _get(self, driver_id: int) -> Driver:
        driver = self.repo.get(driver_id)
        if driver is None:
            raise DriverNotFound(details={"id": driver_id})
        return driver
