"""Test fixtures: isolated SQLite DB + FastAPI TestClient."""

import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_tmp = Path(tempfile.mkdtemp())
TEST_DB_URL = f"sqlite:///{_tmp}/test.db"

import app.database as database  # noqa: E402

database.engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
database.SessionLocal = sessionmaker(bind=database.engine, autoflush=False, autocommit=False)
database.Base.metadata.create_all(bind=database.engine)

from app.main import create_app  # noqa: E402


@pytest.fixture()
def client():
    app = create_app()

    def _override_db():
        db = database.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[database.get_db] = _override_db
    with TestClient(app) as test_client:
        yield test_client
