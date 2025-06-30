from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import Depends, status, HTTPException, Path

from app.db.core import get_db
from app.db.models.users import User

import logging
logger = logging.getLogger(__name__)

class UsersCRUD():
    @staticmethod
    def get_user_id(db: Session , username: str):
        user = db.query(User).filter(User.username == username).one_or_none()
        if user == None:
            raise ValueError('User not found')
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.get(User, user_id)
        if not user:
            raise ValueError('User not found')
        db.delete(user)
        try:
            db.commit()
            logger.info(f'User {user.username} is deleted')
            return {'message': f'User {user.username} is deleted succesfully'}
        except IntegrityError as e:
            db.rollback()
            logger.error(f'Conflict in DB occured: {e}')
            raise RuntimeError()
        except SQLAlchemyError as e:
            db.rollback()
            logger.exception(f'Unexpected error occured in DB: {e}')
            raise RuntimeError()
            