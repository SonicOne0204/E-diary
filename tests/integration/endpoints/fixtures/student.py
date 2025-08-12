import pytest
from sqlalchemy.orm import Session

from app.db.models.types import Student

import logging

logger = logging.getLogger(__name__)


@pytest.fixture()
def create_student_fixture(test_get_db: Session):
    db = test_get_db
    exists = db.query(Student).first()
    if exists:
        logger.info(
            f"Student already exists. Deleted old student and created new one. Student: {exists}"
        )
        db.delete(exists)
        db.commit()
    user = Student(
        username="student",
        hashed_password="$2b$12$TmcwG2s06fQ1qg2VfX5j/e9/3asx/b5UsJBGQvxxnU0QZHK3DZxMu",
        email="student@gmail.com",
        first_name="student",
        last_name="student",
        type="student",
        school_id=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
