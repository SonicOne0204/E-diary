from fastapi import APIRouter, Path, status, HTTPException, Depends
from typing import Annotated
from sqlalchemy.orm import Session

from app.crud.users import UsersCRUD
from app.db.core import get_db
from app.schemas.users import UserOut
from app.exceptions.basic import NotFound


import logging
logger = logging.getLogger(__name__)

users_router = APIRouter(
    prefix='/users',
    tags=['users']
)
                
@users_router.get('/get-id', status_code=status.HTTP_202_ACCEPTED, response_model=UserOut)
def get_id(db: Annotated[Session, Depends(get_db)], username: str):
    try:
        return UsersCRUD.get_user_id(db=db, username=username)
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such user')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error occured')
        
@users_router.delete('/delete/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(db: Annotated[Session, Depends(get_db)], user_id: Annotated[int, Path()]):
    try:
        UsersCRUD.delete_user(db=db, user_id=user_id)
        return {f'User with id {user_id}': 'deleted'}
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such user')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Internal server error occured')
    
