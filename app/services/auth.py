from core.security import verify_password, hash_password, create_access_token
from fastapi import status, Depends
from fastapi import HTTPException
from db.models.users import User
from sqlalchemy.orm import Session
from typing import Annotated
from db.core import get_db
from schemas.auth import Token, Registration_data, Login_data



def login_user(db: Session ,user_data: Login_data) -> Token:
    username = user_data.username
    password = user_data.password
    user = db.query(User).filter(User.username == username).first()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such user')
    verify = verify_password(password, user.hashed_password)
    if verify:
        user_data = {
            'sub': user.username 
        }
        access_token = create_access_token(user_data)
        token = Token(access_token=access_token, token_type='Bearer')
        return token 
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Wrong password')

def register_user(db: Session, user_data: Registration_data):
    username = user_data.username
    password = user_data.password
    role = user_data.role
    user = db.query(User).filter(User.username == username).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists')
    if role < 1 or role > 3: ## role Э(наоборот) [1; 3]    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such role')
    hashed_password = hash_password(password)
    user = User(username = username, hashed_password = hashed_password, role_id = role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
    username: {
            'username': username,
            'role_id': role
        }
    }