from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated
from jose import jwt
from jose.exceptions import JWTError

from app.core.security import verify_password, hash_password, create_access_token
from app.db.models.users import User
from app.db.models.types import Student, Teacher, Principal
from app.db.core import get_async_db
from app.schemas.auth import (
    Token,
    TeacherRegistrationData,
    StudentRegistrationData,
    PrincipalRegistrationData,
)
from app.exceptions.auth import (
    RoleNotAllowed,
    UserExists,
    UserDoesNotExist,
    WrongPassword,
)
from app.core.settings import settings

import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def login_user(db: AsyncSession, user_data: OAuth2PasswordRequestForm) -> Token:
    try:
        username = user_data.username
        password = user_data.password
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user is None:
            raise UserDoesNotExist("User not found")
        verify = verify_password(password, user.hashed_password)
        if verify:
            payload = {"id": user.id, "username": user.username, "role": user.type}
            access_token = create_access_token(payload)
            return Token(access_token=access_token, token_type="Bearer")
        else:
            raise WrongPassword("Wrong password")
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
        raise


async def register_teacher(db: AsyncSession, user_data: TeacherRegistrationData):
    try:
        username = user_data.username
        password = user_data.password
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user:
            raise UserExists()
        if user_data.type == "admin":
            raise RoleNotAllowed("Cannot register as admin. Forbidden")

        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hash_password(user_dict.pop("password"))
        user = Teacher(**user_dict)

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
        await db.rollback()
        raise


async def register_student(db: AsyncSession, user_data: StudentRegistrationData):
    try:
        username = user_data.username
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user:
            raise UserExists()
        if user_data.type == "admin":
            raise RoleNotAllowed("Cannot register as admin")

        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hash_password(user_dict.pop("password"))
        student = Student(**user_dict)

        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
        await db.rollback()
        raise


async def register_principal(db: AsyncSession, user_data: PrincipalRegistrationData):
    try:
        username = user_data.username
        password = user_data.password
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user:
            raise UserExists()
        if user_data.type == "admin":
            raise RoleNotAllowed("Cannot register as admin. Forbidden")

        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hash_password(user_dict.pop("password"))
        principal = Principal(**user_dict)

        db.add(principal)
        await db.commit()
        await db.refresh(principal)
        return principal
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
        await db.rollback()
        raise


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        result = await db.execute(select(User).where(User.id == payload.get("id")))
        user = result.scalar_one_or_none()
        if user is None:
            logger.info(f'User with id {payload["id"]} does not exist')
            raise UserDoesNotExist("User does not exist")
        return user
    except JWTError as e:
        logger.info(f"Invalid token passed: {e}")
        raise
