from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from app.core.security import verify_password, hash_password, create_access_token
from app.db.models.users import User
from app.db.core import get_db
from app.schemas.auth import Token, Registration_data, Login_data



def login_user(db: Session ,user_data: Login_data) -> Token:
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

def register_user(db: Session, user_data: Registration_data):
    username = user_data.username
    password = user_data.password
    type = user_data.type
    user = db.query(User).filter(User.username == username).first()
    if user:
        raise ValueError('User already exists')
    if type == 'admin':    
        raise ValueError('Cannot register as admin. Forbidden')
    hashed_password = hash_password(password)
    user = User(username = username, hashed_password = hashed_password, type = type)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
    username: {
            'username': username,
            'role_id': type
        }
    }