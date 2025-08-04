import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import test_SessionLocal

import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def test_get_db():
    db = test_SessionLocal()
    try:
        yield db
    finally:
        db.close()

