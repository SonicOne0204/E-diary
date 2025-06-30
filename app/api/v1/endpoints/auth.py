from fastapi import status, Depends, APIRouter, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Annotated, Union

import logging 

from app.db.core import get_db
from app.schemas.auth import Token, TeacherRegistrationData, StudentRegistrationData, PrincipalRegistrationData, LoginData
from app.services.auth import login_user, register_student, register_principal, register_teacher
from app.exceptions.auth import RoleNotAllowed, UserExists



auth_router = APIRouter(
    prefix='/auth',
    tags=['authenticaiton']
)

logger = logging.getLogger(__name__)



@auth_router.post('/login', status_code=status.HTTP_200_OK ,response_model=Token)
def login(db: Annotated[Session, Depends(get_db)] ,user_data: LoginData) -> Token:
    try:
        token = login_user(db=db, user_data=user_data)
        return token
    except ValueError as e:
        logger.info(f'Login failed: {e}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f'Exception: Unexpected error occured: {e}')
        raise 

@auth_router.post('/register/teacher', status_code=status.HTTP_201_CREATED)
def registration(db: Annotated[Session, Depends(get_db)], user_data: TeacherRegistrationData):
    try:
        return register_teacher(db=db, user_data=user_data)
    except UserExists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exists')
    except RoleNotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.exception(f'Exception: Unexpected error occured: {e}')
        raise 

@auth_router.post('/register/student', status_code=status.HTTP_201_CREATED)
def registration(db: Annotated[Session, Depends(get_db)], user_data:StudentRegistrationData):
    try:
        return register_student(db=db, user_data=user_data)
    except UserExists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exists')
    except RoleNotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.exception(f'Exception: Unexpected error occured: {e}')
        raise 

@auth_router.post('/register/principal', status_code=status.HTTP_201_CREATED)
def registration(db: Annotated[Session, Depends(get_db)], user_data:PrincipalRegistrationData):
    try:
        return register_principal(db=db, user_data=user_data)
    except UserExists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exists')
    except RoleNotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.exception(f'Exception: Unexpected error occured: {e}')
        raise 