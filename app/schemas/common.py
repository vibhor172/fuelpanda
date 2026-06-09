"""Shared schema building blocks."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base for response DTOs read off ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class TimestampedOut(ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime
