"""Handler base — holds the session and owns the unit-of-work commit."""
from sqlalchemy.orm import Session


class BaseHandler:
    def __init__(self, db: Session) -> None:
        self.db = db

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()
