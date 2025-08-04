import pytest
from sqlalchemy.orm import Session

from app.db.models.schools import School
from app.schemas.grades import GradeSystems

import logging

logger = logging.getLogger(__name__)

@pytest.fixture
def create_school(test_get_db):
    db: Session = test_get_db
    exists: School = db.query(School).first()
    if exists:
        logger.info(f'School already exists. Deleted old School and created new one. School: {exists}')
        db.delete(exists)
        db.commit()
    school = School(name='School', short_name='sc', country='America', address='John Watson street 13', grade_system=GradeSystems.five_num_sys)
    db.add(school)
    db.commit()
    db.refresh(school)
    return school