from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from app.core.security import verify_password, hash_password, create_access_token
from app.db.models.users import User
from app.db.models.types import Student, Teacher, Principal
from app.db.core import get_db
from app.schemas.auth import Token, RegistrationData, LoginData, TeacherRegistrationData, StudentRegistrationData, PrincipalRegistrationData
from app.exceptions.auth import RoleNotAllowed, UserExists



def login_user(db: Session ,user_data: LoginData) -> Token:
    username = user_data.username
    password = user_data.password
    user = db.query(User).filter(User.username == username).first()
    if user == None:
        raise ValueError('User not found')
    verify = verify_password(password, user.hashed_password)
    if verify:
        user_data = {
            'sub': user.username 
        }
        access_token = create_access_token(user_data)
        token = Token(access_token=access_token, token_type='Bearer')
        return token 
    else:
        raise ValueError('Wrong password')

def register_teacher(db: Session, user_data: TeacherRegistrationData):
    username = user_data.username
    password = user_data.password
    user = db.query(User).filter(User.username == username).one_or_none()
    if user:
        raise UserExists()
    if type == 'admin':    
        raise RoleNotAllowed('Cannot register as admin. Forbidden')
    hashed_password = hash_password(password)
    user_dict = user_data.model_dump()
    user_dict['hashed_password'] = user_dict.pop('password')
    user = User(** user_dict)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
    username: {
            'username': username,
            'role_id': type
        }
    }

def register_student(db: Session, user_data: StudentRegistrationData):
    username = user_data.username
    password = user_data.password

    # Check if username already exists
    user = db.query(User).filter(User.username == username).one_or_none()
    if user:
        raise UserExists()

    if user_data.type == 'admin':
        raise RoleNotAllowed("Cannot register as admin")

    user_dict = user_data.model_dump()
    user_dict['hashed_password'] = hash_password(user_dict.pop('password'))

    # ✅ Create Student directly, not User
    student = Student(**user_dict)

    # ✅ Only add and commit once
    db.add(student)
    db.commit()
    db.refresh(student)

    return {
        student.username: {
            'username': student.username
        }
    }

def register_principal(db: Session, user_data: PrincipalRegistrationData):
    username = user_data.username
    password = user_data.password
    user = db.query(User).filter(User.username == username).one_or_none()
    if user:
        raise UserExists()
    if type == 'admin':    
        raise RoleNotAllowed('Cannot register as admin. Forbidden')
    hashed_password = hash_password(password)
    user_dict = user_data.model_dump()
    user_dict['hashed_password'] = user_dict.pop('password')
    user = User(** user_dict)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
    username: {
            'username': username,
            'role_id': type
        }
    }