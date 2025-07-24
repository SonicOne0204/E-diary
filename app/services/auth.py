from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated
from jose import jwt
from jose.exceptions import JWTError

from app.core.security import verify_password, hash_password, create_access_token
from app.db.models.users import User
from app.db.models.types import Student, Teacher, Principal
from app.db.core import get_db
from app.schemas.auth import Token, RegistrationData, LoginData, TeacherRegistrationData, StudentRegistrationData, PrincipalRegistrationData, UserTypes
from app.exceptions.auth import RoleNotAllowed, UserExists, UserDoesNotExist, WrongPassword
from app.core.settings import settings

import logging
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')



def login_user(db: Session ,user_data: OAuth2PasswordRequestForm) -> Token:
    try:
        username = user_data.username
        password = user_data.password
        user = db.query(User).filter(User.username == username).first()
        if user == None:
            raise UserDoesNotExist('User not found')
        verify = verify_password(password, user.hashed_password)
        if verify:
            payload = {
                'id': user.id,
                'username': user.username,
                'role': user.type 
            }
            access_token = create_access_token(payload)
            token = Token(access_token=access_token, token_type='Bearer')
            return token 
        else:
            raise WrongPassword('Wrong password')
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise


def register_teacher(db: Session, user_data: TeacherRegistrationData):
    try:
        username = user_data.username
        password = user_data.password
        user = db.query(User).filter(User.username == username).one_or_none()
        if user:
            raise UserExists()
        if user_data.type == 'admin':    
            raise RoleNotAllowed('Cannot register as admin. Forbidden')
        user_dict = user_data.model_dump()
        user_dict['hashed_password'] = user_dict.pop('password')
        user = Teacher(** user_dict)
        user.hashed_password =  hash_password(password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise
    

def register_student(db: Session, user_data: StudentRegistrationData):
    try:
        username = user_data.username
        password = user_data.password
        user = db.query(User).filter(User.username == username).one_or_none()
        if user:
            raise UserExists()
        if user_data.type == 'admin':
            raise RoleNotAllowed("Cannot register as admin")
        user_dict = user_data.model_dump()
        user_dict['hashed_password'] = hash_password(user_dict.pop('password'))
        student = Student(**user_dict)
        db.add(student)
        db.commit()
        db.refresh(student)
        return student
    except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

def register_principal(db: Session, user_data: PrincipalRegistrationData):
    try:
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
        user = Principal(** user_dict)
        user.hashed_password = hashed_password
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise


def get_current_user(db:Annotated[Session, Depends(get_db)], token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        user = db.query(User).get(payload.get('id'))
        if user == None:
            logger.info(f'User with id {payload["id"]} does not exist')
            raise UserDoesNotExist('User dose not exist')
        return user
    except JWTError as e:
        logger.info(f'Invalid token passed: {e}')
        raise