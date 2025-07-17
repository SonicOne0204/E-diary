from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import Depends, status, HTTPException, Path

from app.db.core import get_db
from app.db.models.users import User
from app.exceptions.basic import NotFound

import logging
logger = logging.getLogger(__name__)

class UsersCRUD():
    @staticmethod
    def get_user_id(db: Session , username: str):
        try:
            user = db.query(User).filter(User.username == username).one_or_none()
            if user == None:
                raise NotFound('User not found')
            return user
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.get(User, user_id)
        if not user:
            raise NotFound('User not found')
        db.delete(user)
        try:
            db.commit()
            logger.info(f'User {user.username} is deleted')
            return {'message': f'User {user.username} is deleted succesfully'}
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Unexpected error occured in DB: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise
            