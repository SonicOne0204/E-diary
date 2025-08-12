from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings

import logging

logger = logging.getLogger(__name__)

engine = create_engine(url=settings.DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        logger.debug("getting db session")
        yield db
    finally:
        logger.debug("closing db session")
        db.close()
