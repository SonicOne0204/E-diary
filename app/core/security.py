from passlib.context import CryptContext
from fastapi import status
from fastapi import HTTPException
from typing import Annotated
from datetime import datetime, timedelta, timezone
from jose import jwt 
from app.core.settings import settings
from app.exceptions.auth import WrongPassword

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hash_password(password) -> str:
    hashed_password = pwd_context.hash(password)
    return hashed_password

def verify_password(plain, hashed) -> bool:
    verifying = pwd_context.verify(plain, hashed)
    if verifying:
        return verifying
    else:
        raise WrongPassword('Wrong password')
    
def create_access_token(data: dict, expiration: timedelta | None = None) -> str: 
    data_copy = data.copy()
    if expiration == None:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=30)
    else:
        expire = datetime.now(tz=timezone.utc) + expiration
    data_copy.update({'exp': expire})
    encoded_token = jwt.encode(data_copy, settings.SECRET_KEY, algorithm='HS256')
    return encoded_token