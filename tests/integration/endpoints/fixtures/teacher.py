import pytest
from sqlalchemy.orm import Session

from tests.conftest import test_SessionLocal
from app.db.models.types import Teacher
from app.db.models.schools import School
from app.schemas.grades import GradeSystems
import logging

logger = logging.getLogger(__name__)


def create_wrong_school(db: Session):
    school = School(
        name="wrong school",
        short_name="ws",
        country="Wrongland",
        address="Wrong street -1",
        grade_system=GradeSystems.five_num_sys,
    )
    db.add(school)
    db.commit()
    return school


def create_teacher_wrong_school(db: Session):
    wrong_school = create_wrong_school(db)
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
        school_id=wrong_school.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def override_get_current_user_teacher_wrong_school():
    db = test_SessionLocal()
    return create_teacher_wrong_school(db)


@pytest.fixture()
def create_teacher_fixture(test_get_db: Session, create_school):
    db = test_get_db
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
        school_id=create_school.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
