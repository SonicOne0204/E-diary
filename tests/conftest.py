import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings
from app.db.models.schools import School
from app.db.core import SessionLocal, Base, get_db
from app.main import app

test_engine = create_engine(settings.TEST_DB_URL)
TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True, scope="function")
def setup_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def get_test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def create_school(get_test_db):
    school = School(
        name="School", short_name="SH", country="China", address="ShiaChan street 32"
    )
    get_test_db.add(school)
    return school


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
