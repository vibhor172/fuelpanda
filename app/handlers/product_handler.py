from sqlalchemy.exc import IntegrityError

from app.core.base_handler import BaseHandler
from app.custom_exceptions.product_exceptions import DuplicateProduct, ProductNotFound
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductHandler(BaseHandler):
    def __init__(self, db, repo: ProductRepository) -> None:
        super().__init__(db)
        self.repo = repo

    def create(self, data: ProductCreate) -> Product:
        if self.repo.get_by_name_or_code(data.name, data.code):
            raise DuplicateProduct(details={"name": data.name, "code": data.code})
        product = Product(**data.model_dump())
        try:
            self.repo.create(product)
            self.commit()
        except IntegrityError:
            self.rollback()
            raise DuplicateProduct(details={"name": data.name, "code": data.code}) from None
        return product

    def update(self, product_id: int, data: ProductUpdate) -> Product:
        product = self._get(product_id)
        try:
            self.repo.update(product, data.model_dump(exclude_unset=True))
            self.commit()
        except IntegrityError:
            self.rollback()
            raise DuplicateProduct() from None
        return product

    def get(self, product_id: int) -> Product:
        return self._get(product_id)

    def list(self, *, limit: int, offset: int) -> list[Product]:
        return self.repo.list(limit=limit, offset=offset)

    def _get(self, product_id: int) -> Product:
        product = self.repo.get(product_id)
        if product is None:
            raise ProductNotFound(details={"id": product_id})
        return product
