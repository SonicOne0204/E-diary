import pytest
from sqlalchemy.orm import Session

from app.db.models.subjects import Subject


@pytest.fixture()
def create_subject(test_get_db: Session, create_school):
    db = test_get_db
    subject = Subject(name="History", school_id=create_school.id)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject
