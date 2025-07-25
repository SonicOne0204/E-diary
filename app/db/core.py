from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings

import logging
logger = logging.getLogger(__name__)

engine = create_engine(url=settings.DB_URL)
session_bind = sessionmaker(bind=engine)
model = declarative_base()

def get_db():
    try:
        logger.debug('getting db session')
        db = session_bind()
        yield db
    finally:
        logger.debug('closing db session')
        db.close()
