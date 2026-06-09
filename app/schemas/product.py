from pydantic import BaseModel, Field

from app.schemas.common import TimestampedOut


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=64)
    unit: str = Field(default="gallons", max_length=32)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=64)
    unit: str | None = Field(default=None, max_length=32)


class ProductOut(TimestampedOut):
    name: str
    code: str
    unit: str
