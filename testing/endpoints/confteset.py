import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


from app.testing.conftest import _test_session_bind
from app.db.models.users import User
from app.db.models.schools import School
from app.schemas.grades import GradeSystems
from app.services.auth import get_current_user
from app.main import app 

def create_admin(db: Session):
    user = User(
        username='admin', 
        hashed_password='$2b$12$TmcwG2s06fQ1qg2VfX5j/e9/3asx/b5UsJBGQvxxnU0QZHK3DZxMu', 
        email='admin@gmail.com', 
        first_name='admin', 
        last_name='admin', 
        type='admin'
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_teacher(db: Session):
    user = User(
        username='teacher', 
        hashed_password='$2b$12$TmcwG2s06fQ1qg2VfX5j/e9/3asx/b5UsJBGQvxxnU0QZHK3DZxMu', 
        email='teacher@gmail.com', 
        first_name='teacher', 
        last_name='teacher', 
        type='teacher'
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture()
def test_get_db():
    db: Session = _test_session_bind()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def test_client():
    test_client = TestClient(app=app)
    return test_client 

@pytest.fixture()
def create_superuser(test_get_db):
    return create_admin(test_get_db)

@pytest.fixture()
def create_school(test_get_db):
    school = School(name='School', short_name='sc', country='America', address='John Watson street 13', grade_system=GradeSystems.five_num_sys)
    db: Session = test_get_db
    db.add(school)
    db.commit()
    db.refresh(school)
    return school

def override_get_current_user_admin():
    return create_admin()

def override_get_current_user_teacher():
    return create_teacher()


app.dependency_overrides[get_current_user] = override_get_current_user_admin