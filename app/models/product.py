from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    unit: Mapped[str] = mapped_column(String(32), nullable=False, default="gallons")
