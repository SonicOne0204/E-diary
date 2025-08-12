import pytest
from sqlalchemy.orm import Session

from app.db.models.users import User
from app.db.models.types import Teacher
from app.services.auth import get_current_user
from app.main import app


import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def create_superuser(test_get_db: Session):
    admin = User(
        username="admin",
        hashed_password="$2b$12$ULo0.9l6SqOWQvBEbu4FTuYuuj6lkMhh5ytnfFgnw7LH/u1.QXOEu",
        email="admin@admin",
        first_name="admin",
        last_name="admin",
        type="admin",
    )
    test_get_db.add(admin)
    test_get_db.commit()
    return admin


def create_admin(db: Session):
    exists = db.query(User).first()
    if exists:
        logger.info(
            f"User already exists. Deleted old user and created new one. User: {exists}"
        )
        db.delete(exists)
        db.commit()
    user = User(
        username="admin",
        hashed_password="$2b$12$TmcwG2s06fQ1qg2VfX5j/e9/3asx/b5UsJBGQvxxnU0QZHK3DZxMu",
        email="admin@gmail.com",
        first_name="admin",
        last_name="admin",
        type="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_teacher(db: Session):
    exists = db.query(Teacher).first()
    if exists:
        logger.info(
            f"Teacher already exists. Deleted old teacher and created new one. Teacher: {exists}"
        )
        db.delete(exists)
        db.commit()
    user = Teacher(
        username="teacher",
        hashed_password="$2b$12$TmcwG2s06fQ1qg2VfX5j/e9/3asx/b5UsJBGQvxxnU0QZHK3DZxMu",
        email="teacher@gmail.com",
        first_name="teacher",
        last_name="teacher",
        type="teacher",
        school_id=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def override_get_current_user_teacher(db: Session):
    return create_teacher(db)


def override_get_current_user_admin(db: Session):
    return create_admin(db)


app.dependency_overrides[get_current_user] = override_get_current_user_admin
