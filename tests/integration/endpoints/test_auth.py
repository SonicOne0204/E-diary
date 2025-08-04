from sqlalchemy.orm import Session

from app.main import app
from app.db.models.users import User
from app.db.models.types import Teacher, Principal, Student
from app.core.security import verify_password
from app.services.auth import get_current_user
from tests.integration.endpoints.fixtures import (override_get_current_user_teacher, override_get_current_user_admin)



def test_for_login_access_token(test_client, create_superuser):
    response = test_client.post('/auth/login', data={'username': 'admin', 'password': 'admin'})
    data = response.json()
    assert (
        "access_token" in data
        and data["token_type"] == "Bearer"
        and response.status_code == 200
    )

def test_for_principal_registration(test_client, create_school, test_get_db):
    response = test_client.post(
        '/auth/register/principal',
        json={
            'username': 'principal',
            'password': 'principal',
            'email': 'principal@gmail.com',
            'first_name': 'Lui',
            'last_name': 'Watson',
            'type': 'principal',
            'school_id': create_school.id
        }
    )
    assert response.status_code == 201
    
    data = response.json()

    assert data['username'] == 'principal'
    assert data['email'] == 'principal@gmail.com'
    user_in_db: User = test_get_db.query(User).filter(User.username == 'principal').first()
    principal_in_db: Principal = test_get_db.query(Principal).get(user_in_db.id)
    assert data['school_id'] == principal_in_db.school_id
    assert user_in_db is not None
    assert verify_password('principal', user_in_db.hashed_password)

def test_for_principal_registration_role_not_allowed_error(test_client, create_school):
    try:
        app.dependency_overrides[get_current_user] = override_get_current_user_teacher
        response = test_client.post(
            '/auth/register/principal',
            json={
                'username': 'principal',
                'password': 'principal',
                'email': 'principal@gmail.com',
                'first_name': 'Lui',
                'last_name': 'Watson',
                'type': 'principal',
                'school_id': create_school.id
            }
        )
        assert response.status_code == 403
    finally:
        app.dependency_overrides[get_current_user] = override_get_current_user_admin
