"""SQLAlchemy engine, SessionLocal, and the per-request get_db() dependency.

The engine is created lazily so importing the app (e.g. for unit tests with
mocked repositories) doesn't require a live DB driver/connection.
"""
from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.dependencies.config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    connect_args: dict = {}
    if settings.database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(
        settings.database_url, pool_pre_ping=True, future=True, connect_args=connect_args
    )


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(), autoflush=False, expire_on_commit=False, future=True
    )


def get_db() -> Generator[Session, None, None]:
    """Yield one Session per request. The handler owns commit/rollback."""
    db = get_sessionmaker()()
    try:
        yield db
    finally:
        db.close()
