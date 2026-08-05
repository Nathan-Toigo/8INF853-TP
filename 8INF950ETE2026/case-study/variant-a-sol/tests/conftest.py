import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


TEST_DATABASE_PATH = Path("test_medical_appointments.db")
os.environ["DATABASE_URL"] = f"sqlite:///./{TEST_DATABASE_PATH}"


from app.database import Base, engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

    if TEST_DATABASE_PATH.exists():
        TEST_DATABASE_PATH.unlink()


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
