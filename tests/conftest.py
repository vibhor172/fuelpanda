"""Shared fixtures.

The integration suite runs against an in-memory SQLite database (StaticPool so
all sessions share one DB) and fakeredis, wired in via FastAPI dependency
overrides. Production targets Postgres + Redis (see docker-compose.yml); the
partial unique indexes that enforce vehicle blocking are emitted on SQLite too
(`sqlite_where`), so the blocking rule is exercised here as well.
"""
import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.core.base_model import Base
from app.dependencies.database import get_db
from app.dependencies.redis_client import get_redis
from app.main import app


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def db_session(engine):
    TestingSession = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False, future=True
    )
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def fake_redis():
    return fakeredis.FakeStrictRedis(decode_responses=True)


@pytest.fixture
def client(engine, fake_redis):
    TestingSession = sessionmaker(
        bind=engine, autoflush=False, expire_on_commit=False, future=True
    )

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    def override_get_redis():
        return fake_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
