import pytest
from sqlalchemy.orm import Session

from app.db.models.groups import Group


@pytest.fixture()
def create_group(test_get_db: Session, create_school):
    db = test_get_db
    group = Group(school_id=create_school.id, grade="5", grade_section="A")
    db.add(group)
    db.commit()
    db.refresh(group)
    return group
