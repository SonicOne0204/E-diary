from app.schemas.grades import GradeSystems
from app.db.models.types import Teacher
from tests.integration.endpoints.fixtures.teacher import (
    override_get_current_user_teacher_wrong_school,
)
from tests.integration.conftest import (
    override_get_current_user_teacher,
    override_get_current_user_admin,
)
from app.services.auth import get_current_user
from app.main import app


def test_assign_grade(
    test_get_db, test_client, create_schedule, create_student_fixture
):
    try:
        app.dependency_overrides[get_current_user] = override_get_current_user_teacher
        user = override_get_current_user_teacher(test_get_db)
        teacher = test_get_db.query(Teacher).get(user.id)
        response = test_client.post(
            "/teacher/assign-grade",
            json={
                "grade_system": GradeSystems.five_num_sys,
                "value_numeric": 5,
                "schedule_id": create_schedule.id,
                "student_id": create_student_fixture.id,
            },
        )
        data = response.json()
        assert response.status_code == 200

        assert data["value_letter"] == None and data["value_boolean"] == None
        assert create_student_fixture.school_id == teacher.school_id
    finally:
        app.dependency_overrides[get_current_user] = override_get_current_user_admin


def test_assign_grade_wrong_school(
    test_get_db, test_client, create_schedule, create_student_fixture
):
    try:
        app.dependency_overrides[get_current_user] = (
            override_get_current_user_teacher_wrong_school
        )
        user = override_get_current_user_teacher_wrong_school(test_get_db)
        teacher = test_get_db.query(Teacher).get(user.id)
        response = test_client.post(
            "/teacher/assign-grade",
            json={
                "grade_system": GradeSystems.five_num_sys,
                "value_numeric": 5,
                "schedule_id": create_schedule.id,
                "student_id": create_student_fixture.id,
            },
        )
        data = response.json()
        assert response.status_code == 200

        assert data["value_letter"] == None and data["value_boolean"] == None
        assert create_student_fixture.school_id == teacher.school_id
    finally:
        app.dependency_overrides[get_current_user] = override_get_current_user_admin
