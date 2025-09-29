import pytest
from httpx import AsyncClient
from app.schemas.users import UserTypes
from app.db.models.types import Student
from app.db.models.users import User
from app.main import app
from app.services.auth import get_current_user


@pytest.mark.anyio(backends=["asyncio"])
async def test_register_principal_success(client: AsyncClient, db_session):
    response = await client.post(
        "/schools/",
        json={
            "name": "school",
            "short_name": "sh",
            "country": "Russia",
            "address": "Igrushka street 12",
            "grade_system": "5numerical",
        },
    )

    school_id = response.json()["id"]
    payload = {
        "username": "principal1",
        "first_name": "John",
        "last_name": "Doe",
        "email": "principal1@example.com",
        "password": "strongpassword123",
        "school_id": school_id,
    }

    response = await client.post("/auth/register/principals/", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert "id" in data
    assert data.get("type") == UserTypes.principal


@pytest.mark.anyio(backends=["asyncio"])
async def test_register_principal_wrong_role(client: AsyncClient, db_session):
    """Should fail when current user is a Student instead of Admin."""

    async def fake_current_user():
        return Student(
            username="student1",
            first_name="Alice",
            last_name="Smith",
            email="student1@example.com",
            hashed_password="eyJhbGciOiJIUzI1NiJ9.YWRtaW4.6EzPzEdawDoa2A4x43oai7sdtPQUUtbR8eXtfJqmSyU",  # password is admin
        )

    app.dependency_overrides[get_current_user] = fake_current_user

    try:
        payload = {
            "username": "principal2",
            "first_name": "Bob",
            "last_name": "Brown",
            "email": "principal2@example.com",
            "password": "strongpassword123",
        }

        response = await client.post("/auth/register/principals/", json=payload)
        assert response.status_code in (401, 403)
        data = response.json()
        assert "detail" in data

    finally:
        app.dependency_overrides.clear()


@pytest.mark.anyio(backends=["asyncio"])
async def test_login_success(client: AsyncClient, db_session):
    """Test successful login of a user"""
    user_data = {
        "username": "loginuser",
        "first_name": "Test",
        "last_name": "User",
        "email": "loginuser@example.com",
        "password": "password123",
    }
    response = await client.post("/auth/register/students/", json=user_data)
    user_id = response.json()["id"]

    app.dependency_overrides[get_current_user] = db_session.get(User, user_id)

    payload = {"username": "loginuser", "password": "password123"}

    response = await client.post(
        "/auth/login/",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.anyio(backends=["asyncio"])
async def test_login_wrong_password(client: AsyncClient, db_session):
    """Test login fails with incorrect password"""
    try:
        user_data = {
            "username": "wrongpassuser",
            "first_name": "Test",
            "last_name": "User",
            "email": "wrongpassuser@example.com",
            "password": "correctpassword",
        }
        response = await client.post("auth/register/students/", json=user_data)
        user_id = response.json()["id"]

        app.dependency_overrides[get_current_user] = db_session.get(User, user_id)

        payload = {"username": "wrongpassuser", "password": "wrongpassword"}

        response = await client.post(
            "/auth/login/",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        data = response.json()
        assert response.status_code == 401
        assert "detail" in data
    finally:
        app.dependency_overrides.clear()
