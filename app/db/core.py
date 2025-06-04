from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings

engine = create_engine(url=settings.DB_URL)
session_bind = sessionmaker(bind=engine)
model = declarative_base()

def get_db():
    try:
        db = session_bind()
        yield db
    finally:
        db.close()