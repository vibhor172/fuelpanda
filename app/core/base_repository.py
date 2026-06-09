"""Generic CRUD repository (Template Method + Generics)."""
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.base_model import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    """Persistence skeleton. Subclasses set `model` and add specific reads.

    Repositories never commit — the handler owns the unit of work.
    """

    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, id_: int) -> ModelT | None:
        return self.db.get(self.model, id_)

    def get_for_update(self, id_: int) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == id_).with_for_update()
        return self.db.execute(stmt).scalar_one_or_none()

    def list(self, *, limit: int = 50, offset: int = 0, **filters: Any) -> list[ModelT]:
        stmt = select(self.model)
        for field, value in filters.items():
            if value is not None:
                stmt = stmt.where(getattr(self.model, field) == value)
        stmt = stmt.order_by(self.model.id).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.flush()
        return obj

    def update(self, obj: ModelT, data: dict[str, Any]) -> ModelT:
        for key, value in data.items():
            setattr(obj, key, value)
        self.db.flush()
        return obj

    def delete(self, obj: ModelT) -> None:
        self.db.delete(obj)
        self.db.flush()
