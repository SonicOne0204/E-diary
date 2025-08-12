import pytest
from sqlalchemy.orm import Session
from datetime import datetime

from app.schemas.schedules import Week
from app.db.models.schedules import Schedule


@pytest.fixture()
def create_schedule(
    test_get_db: Session,
    create_school,
    create_group,
    create_subject,
    create_teacher_fixture,
):
    db = test_get_db
    schedule = Schedule(
        group_id=create_group.id,
        school_id=create_school.id,
        subject_id=create_subject.id,
        teacher_id=create_teacher_fixture.id,
        day_of_week=Week.monday,
        start_time=datetime(year=2025, month=4, day=2, hour=12, minute=30),
        end_time=datetime(year=2025, month=4, day=2, hour=14, minute=30),
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule
