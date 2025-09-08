import pytest

from app.db.models.users import User
from app.db.models.types import Teacher, Student
from app.services.auth import get_current_user
from httpx import AsyncClient, ASGITransport
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

app.dependency_overrides[get_current_user] = override_user_admin

@pytest.mark.asyncio
async def test_principal_registration(create_school):
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        response = await client.post(
            "auth/register/principals",
            json={
                "username": "principal",
                "password": "principal",
                "email": "pricnipal@gmail.com",
                "first_name": "John",
                "last_name": "Doe",
                "school_id": create_school.id
            },
        )
    response_json = response.json()
    assert response.status_code == 201
    assert response_json["type"] == "principal"

@pytest.mark.asyncio
async def test_principal_registration_wrong_role(create_school):
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            app.dependency_overrides[get_current_user] = override_user_teacher
            response = await client.post(
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

@pytest.mark.asyncio
async def test_school_crud():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        response_post = await client.post(
            "/schools/",
            json={
                "name": "school",
                "short_name": "sh",
                "country": "France",
                "address": "Juan Pero street 61",
                "grade_system": "letter"
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
