from sqlalchemy import Enum, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base_model import BaseModel
from app.dependencies.constants import LocationType


class Location(BaseModel):
    __tablename__ = "locations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[LocationType] = mapped_column(
        Enum(LocationType, name="location_type"), nullable=False
    )
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)

    __table_args__ = (Index("ix_locations_type", "type"),)
