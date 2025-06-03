from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from db.core import get_db
from fastapi import status, HTTPException, Path
from db.models.users import User

def get_user_id(db: Annotated[Session, Depends(get_db)] , username: str):
    user = db.query(User).filter(User.username == username).one_or_none()
    return { 'user_id': user.id }

def delete_user(db: Annotated[Session, Depends(get_db)], user_id: Annotated[int, Path()]):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(user)
    db.commit()