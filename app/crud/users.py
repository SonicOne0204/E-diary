from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.core import get_db
from fastapi import status, HTTPException, Path
from app.db.models.users import User

def get_user_id(db: Session , username: str):
    user = db.query(User).filter(User.username == username).one_or_none()
    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such user')
    return { 'user_id': user.id }

def delete_user(db: Session, user_id: int):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(user)
    db.commit()