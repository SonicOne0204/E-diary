from fastapi import APIRouter
from fastapi import status, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from db.core import get_db
from schemas.auth import Token, Registration_data, Login_data
from services.auth import login_user, register_user
auth_router = APIRouter(
    prefix='/auth',
    tags=['authenticaiton']
)

@auth_router.post('/login', response_model=Token)
def login(db: Annotated[Session, Depends(get_db)] ,user_data: Login_data) -> Token:
    return login_user(db=db, user_data=user_data)

@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
def registration(db: Annotated[Session, Depends(get_db)], user_data: Registration_data):
    return register_user(db=db, user_data=user_data)

