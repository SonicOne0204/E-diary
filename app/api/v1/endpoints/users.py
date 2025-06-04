from fastapi import APIRouter, Path, status, HTTPException, Depends
from app.crud.users import delete_user, get_user_id
from typing import Annotated
from sqlalchemy.orm import Session
from app.db.core import get_db

users_router = APIRouter(
    prefix='/users',
    tags=['users']
)

@users_router.get('/get-id', status_code=status.HTTP_202_ACCEPTED)
def get_id(db: Annotated[Session, Depends(get_db)], username: str):
    return get_user_id(db=db, username=username)

@users_router.delete('/delete/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(db: Annotated[Session, Depends(get_db)], user_id: Annotated[int, Path()]):
    delete_user(db=db, user_id=user_id)