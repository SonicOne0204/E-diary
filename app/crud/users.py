from sqlalchemy.orm import Session, with_polymorphic
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.users import User
from app.exceptions.basic import NotFound

import logging

logger = logging.getLogger(__name__)


class UsersCRUD:
    @staticmethod
    def get_users(db: Session, page: int, limit: int, username: str | None = None):
        try:
            offset = (page - 1) * limit
            if username:
                users = db.query(User).filter(User.username == username).all()
                if not users:
                    raise NotFound("User not found")
            else:
                users = (
                    db.query(with_polymorphic(User, []))
                    .offset(offset)
                    .limit(limit)
                    .all()
                )
            return users
        except Exception as e:
            logger.exception(f"Unexpected error occured: {e}")
            raise

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.get(User, user_id)
        if not user:
            raise NotFound("User not found")
        db.delete(user)
        try:
            db.commit()
            logger.info(f"User {user.username} is deleted")
            return {"message": f"User {user.username} is deleted succesfully"}
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Unexpected error occured in DB: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occured: {e}")
            raise
