from sqlalchemy.orm import with_polymorphic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.users import User
from app.exceptions.basic import NotFound

import logging

logger = logging.getLogger(__name__)


class UsersCRUD:
    @staticmethod
    async def get_users(db: AsyncSession, page: int, limit: int, username: str | None = None):
        try:
            offset = (page - 1) * limit
            if username:
                result = await db.execute(select(User).where(User.username == username))
                users = result.scalars().all()
                if not users:
                    raise NotFound("User not found")
            else:
                stmt = select(with_polymorphic(User, [])).offset(offset).limit(limit)
                result = await db.execute(stmt)
                users = result.scalars().all()
            return users
        except SQLAlchemyError as e:
            logger.error(f"DB error occurred: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int):
        try:
            user = await db.get(User, user_id)
            if not user:
                raise NotFound("User not found")

            await db.delete(user)
            await db.commit()
            logger.info(f"User {user.username} is deleted")
            return {"message": f"User {user.username} is deleted successfully"}
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"DB error occurred: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise
