import pytest

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.core import Base, get_db
from app.core.settings import settings

import logging
logger = logging.getLogger(__name__)

test_engine = create_engine(url=settings.TEST_DB_URL)
test_SessionLocal = sessionmaker(bind=test_engine, autoflush=False)

def override_get_db():
    db = test_SessionLocal()
    try:
        yield db
    finally:
        logger.debug('closing db session')
        db.close()

@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

app.dependency_overrides[get_db] = override_get_db