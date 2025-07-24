from fastapi import status, Depends, APIRouter, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Annotated, Union
from fastapi.security import OAuth2PasswordRequestForm

import logging 

from app.db.core import get_db
from app.db.models.types import Teacher,Student,Principal
from app.schemas.auth import Token, TeacherRegistrationData, StudentRegistrationData, PrincipalRegistrationData, LoginData, RegistrationDataOut, UserTypes
from app.services.auth import login_user, register_student, register_principal, register_teacher
from app.exceptions.auth import RoleNotAllowed, UserExists, UserDoesNotExist, WrongPassword
from app.dependecies.auth import check_role


auth_router = APIRouter(
    prefix='/auth',
    tags=['authenticaiton']
)

logger = logging.getLogger(__name__)



@auth_router.post('/login', status_code=status.HTTP_200_OK ,response_model=Token)
def login(db: Annotated[Session, Depends(get_db)] ,user_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    try:
        token = login_user(db=db, user_data=user_data)
        return token
    except WrongPassword as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except UserDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 

@auth_router.post('/register/teacher', status_code=status.HTTP_201_CREATED, response_model=RegistrationDataOut)
def registration(db: Annotated[Session, Depends(get_db)], user_data: TeacherRegistrationData) -> Teacher:
    try:
        return register_teacher(db=db, user_data=user_data)
    except UserExists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exists')
    except RoleNotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 

@auth_router.post('/register/student', status_code=status.HTTP_201_CREATED, response_model=RegistrationDataOut)
def registration(db: Annotated[Session, Depends(get_db)], user_data:StudentRegistrationData) -> Student:
    try:
        return register_student(db=db, user_data=user_data)
    except UserExists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exists')
    except RoleNotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 

@auth_router.post('/register/principal', status_code=status.HTTP_201_CREATED, response_model=RegistrationDataOut, dependencies=[Depends(check_role(UserTypes.admin))])
def registration(db: Annotated[Session, Depends(get_db)], user_data:PrincipalRegistrationData) -> Principal:
    try:
        return register_principal(db=db, user_data=user_data)
    except UserExists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exists')
    except RoleNotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) 