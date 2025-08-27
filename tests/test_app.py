
from app.db.models.users import User
from app.db.models.types import Teacher, Student
from app.services.auth import get_current_user
from fastapi.testclient import TestClient
from app.main import app


def override_user_admin():
    user = User(
        username="admin",
        hashed_password="$2b$12$1SZso.p2QgBZzkuojqoyB.LSwbFV4yCVGChSn7DfdO2OpktnedDnW",
        first_name="John",
        last_name="Doe",
        email="admin@gmail.com",
    )  # password is admin
    return user


def override_user_teacher():
    user = Teacher(
        username="teacher",
        hashed_password="$2b$12$1SZso.p2QgBZzkuojqoyB.LSwbFV4yCVGChSn7DfdO2OpktnedDnW",
        first_name="John",
        last_name="Doe",
        email="teacher@gmail.com",
    )  # password is still admin
    return user


def override_user_student():
    user = Student(
        username="student",
        hashed_password="$2b$12$1SZso.p2QgBZzkuojqoyB.LSwbFV4yCVGChSn7DfdO2OpktnedDnW",
        first_name="John",
        last_name="Doe",
        email="student@gmail.com",
    )  # password is still admin
    return user


client = TestClient(app=app)

app.dependency_overrides[get_current_user] = override_user_admin


def test_principal_registration(create_school):
    response = client.post(
        "auth/register/principals",
        json={
            "username": "principal",
            "password": "principal",
            "email": "pricnipal@gmail.com",
            "first_name": "John",
            "last_name": "Doe",
            "school_id": create_school.id,
        },
    )
    response_json = response.json()
    assert response.status_code == 201
    assert response_json["type"] == "principal"


def test_principal_registration_wrong_role(create_school):
    try:
        app.dependency_overrides[get_current_user] = override_user_teacher
        response = client.post(
            "auth/register/principals",
            json={
                "username": "principal",
                "password": "principal",
                "email": "pricnipal@gmail.com",
                "first_name": "John",
                "last_name": "Doe",
                "school_id": create_school.id,
            },
        )
        assert response.status_code == 403
    finally:
        app.dependency_overrides[get_current_user] = override_user_admin


def test_school_crud():
    response_post = client.post(
        "/schools/",
        json={
            "name": "school",
            "short_name": "sh",
            "country": "France",
            "address": "Juan Pero street 61",
        },
    )
    assert response_post.status_code == 201
    created_school = response_post.json()
    school_id = created_school["id"]
    response_get = client.get(f"/schools/{school_id}")
    assert response_get.status_code == 200
    school_data = response_get.json()
    assert school_data["name"] == "school"
    assert school_data["country"] == "France"

    response_patch = client.patch(
        f"/schools/{school_id}", json={"name": "updated school"}
    )
    assert response_patch.status_code == 200
    updated_data = response_patch.json()
    assert updated_data["name"] == "updated school"

    response_bulk = client.get("/schools/")
    assert response_bulk.status_code == 200
    all_schools = response_bulk.json()
    assert isinstance(all_schools, list)
    assert any(s["id"] == school_id for s in all_schools)
