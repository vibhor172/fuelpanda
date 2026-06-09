from sqlalchemy import or_, select

from app.core.base_repository import BaseRepository
from app.models.product import Product


class ProductRepository(BaseRepository[Product]):
    model = Product

    def get_by_name_or_code(self, name: str, code: str) -> Product | None:
        stmt = select(Product).where(or_(Product.name == name, Product.code == code))
        return self.db.execute(stmt).scalars().first()
