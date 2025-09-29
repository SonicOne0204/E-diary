from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select

from app.schemas.groups import GroupData
from app.db.models.groups import Group
from app.exceptions.basic import NotFound, NotAllowed
from app.db.models.users import User
from app.db.models.types import Principal
from app.schemas.users import UserTypes

import logging

logger = logging.getLogger(__name__)


class GroupCRUD:
    @staticmethod
    async def add_group(db: AsyncSession, user: User, data: GroupData):
        try:
            if user.type == UserTypes.principal:
                principal: Principal | None = await db.get(Principal, user.id)
                if not principal or principal.school_id != data.school_id:
                    logger.warning(
                        f"User with id {user.id} tried to create group in school with id {data.school_id}. Not allowed"
                    )
                    raise NotAllowed("Cannot access other schools")

            group = Group()
            for key, value in data.model_dump().items():
                setattr(group, key, value)

            db.add(group)
            await db.commit()
            await db.refresh(group)
            return group
        except IntegrityError:
            await db.rollback()
            raise
        except SQLAlchemyError:
            await db.rollback()
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def delete_group(db: AsyncSession, user: User, group_id: int):
        try:
            group: Group | None = await db.get(Group, group_id)
            if not group:
                logger.info(f"Group with id {group_id} not found")
                raise NotFound("Group not found")

            if user.type == UserTypes.principal:
                principal: Principal | None = await db.get(Principal, user.id)
                if not principal or principal.school_id != group.school_id:
                    logger.warning(
                        f"User with id {user.id} tried to delete group in school with id {group.school_id}. Not allowed"
                    )
                    raise NotAllowed("Cannot access other schools")

            await db.delete(group)
            await db.commit()
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
            await db.rollback()
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def update_group(
        db: AsyncSession, user: User, group_id: int, data: GroupData
    ):
        try:
            group: Group | None = await db.get(Group, group_id)
            if not group:
                logger.info(f"Group with id {group_id} not found")
                raise NotFound("Group not found")

            if user.type == UserTypes.principal:
                principal: Principal | None = await db.get(Principal, user.id)
                if not principal or principal.school_id != group.school_id:
                    logger.warning(
                        f"User with id {user.id} tried to update group in school with id {group.school_id}. Not allowed"
                    )
                    raise NotAllowed("Cannot access other schools")

            for key, value in data.model_dump().items():
                setattr(group, key, value)

            await db.commit()
            await db.refresh(group)
            return group
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
            await db.rollback()
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def get_groups(db: AsyncSession, user: User, school_id: int):
        try:
            result = await db.execute(select(Group).where(Group.school_id == school_id))
            groups = result.scalars().all()
            if not groups:
                logger.info(f"Groups with school id {school_id} not found")
                raise NotFound("Groups not found")

            if user.type == UserTypes.principal:
                principal: Principal | None = await db.get(Principal, user.id)
                if not principal or principal.school_id != school_id:
                    logger.warning(
                        f"User with id {user.id} tried to get groups in school with id {school_id}. Not allowed"
                    )
                    raise NotAllowed("Cannot access other schools")

            return groups
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def get_group(db: AsyncSession, user: User, group_id: int):
        try:
            group: Group | None = await db.get(Group, group_id)
            if not group:
                logger.info(f"Group with id {group_id} not found")
                raise NotFound("Group not found")

            if user.type == UserTypes.principal:
                principal: Principal | None = await db.get(Principal, user.id)
                if not principal or principal.school_id != group.school_id:
                    logger.warning(
                        f"User with id {user.id} tried to get group in school with id {group.school_id}. Not allowed"
                    )
                    raise NotAllowed("Cannot access other schools")

            return group
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            raise
