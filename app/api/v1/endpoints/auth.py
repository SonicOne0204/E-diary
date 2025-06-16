from fastapi import status, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

import logging 

from app.db.core import get_db
from app.schemas.auth import Token, Registration_data, Login_data
from app.services.auth import login_user, register_user


auth_router = APIRouter(
    prefix='/auth',
    tags=['authenticaiton']
)

logger = logging.getLogger(__name__)

@auth_router.post('/login', status_code=status.HTTP_200_OK ,response_model=Token)
def login(db: Annotated[Session, Depends(get_db)] ,user_data: Login_data) -> Token:
    try:
        token = login_user(db=db, user_data=user_data)
        return token
    except ValueError as e:
        logger.info(f'Login failed: {e}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f'Exception: Unexpected error occured: {e}')
        raise 

@auth_router.post('/register', status_code=status.HTTP_201_CREATED)
def registration(db: Annotated[Session, Depends(get_db)], user_data: Registration_data):
    try:
        return register_user(db=db, user_data=user_data)
    except ValueError as e:
        logger.info(f'Registration failed: {e}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception(f'Exception: Unexpected error occured: {e}')
        raise 
