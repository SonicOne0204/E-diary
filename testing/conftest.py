import pytest
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine


from app.core.settings import settings
from app.db.core import get_db, model
from app.main import app 


import logging
logger = logging.getLogger(__name__)

_test_engine = create_engine(settings.DB_URL, echo=False)
_test_session_bind = sessionmaker(bind=_test_engine)


def override_get_db():
    db: Session = _test_session_bind()
    try:
        logger.debug('starting db test session')
        yield db
    finally:
        logger.debug('closed db test session')
        db.close()

  

@pytest.fixture(autouse=True)
def reset_db():
    model.metadata.drop_all(bind=_test_engine)
    model.metadata.create_all(bind=_test_engine)
    logger.debug('resetted test db session')
    yield





app.dependency_overrides[get_db] = override_get_db
        