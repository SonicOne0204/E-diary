from fastapi import status, Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

import logging

from app.db.core import get_async_db
from app.db.models.types import Teacher, Student, Principal
from app.schemas.auth import (
    Token,
    TeacherRegistrationData,
    StudentRegistrationData,
    PrincipalRegistrationData,
    RegistrationDataOut,
    UserTypes,
    PrincipalRegistrationDataOut,
)
from app.services.auth import (
    login_user,
    register_student,
    register_principal,
    register_teacher,
)
from app.exceptions.auth import (
    RoleNotAllowed,
    UserExists,
    UserDoesNotExist,
    WrongPassword,
)
from app.dependecies.auth import check_role


auth_router = APIRouter(prefix="/auth", tags=["authentication"])

logger = logging.getLogger(__name__)


@auth_router.post("/login/", status_code=status.HTTP_200_OK, response_model=Token)
async def login(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    try:
        token = await login_user(db=db, user_data=user_data)
        return token
    except WrongPassword as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except UserDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error during login: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth_router.post(
    "/register/teachers/",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationDataOut,
)
async def registration_teacher(
    db: Annotated[AsyncSession, Depends(get_async_db)], user_data: TeacherRegistrationData
) -> Teacher:
    try:
        return await register_teacher(db=db, user_data=user_data)
    except UserExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )
    except RoleNotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.exception(f"Unexpected error during teacher registration: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth_router.post(
    "/register/students/",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationDataOut,
)
async def registration_student(
    db: Annotated[AsyncSession, Depends(get_async_db)], user_data: StudentRegistrationData
) -> Student:
    try:
        return await register_student(db=db, user_data=user_data)
    except UserExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )
    except RoleNotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.exception(f"Unexpected error during student registration: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@auth_router.post(
    "/register/principals/",
    status_code=status.HTTP_201_CREATED,
    response_model=PrincipalRegistrationDataOut,
    dependencies=[Depends(check_role(UserTypes.admin))],
)
async def registration_principal(
    db: Annotated[AsyncSession, Depends(get_async_db)], user_data: PrincipalRegistrationData
) -> Principal:
    try:
        return await register_principal(db=db, user_data=user_data)
    except UserExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )
    except RoleNotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        logger.exception(f"Unexpected error during principal registration: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
