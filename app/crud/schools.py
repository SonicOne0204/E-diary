from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import select

from app.db.models.schools import School
from app.schemas.schools import SchoolData, SchoolUpdate
from app.schemas.users import UserTypes
from app.exceptions.basic import NotFound, NotAllowed
from app.db.models.users import User
from app.db.models.types import Teacher, Student, Principal

import logging

logger = logging.getLogger(__name__)


class SchoolCRUD:
    @staticmethod
    async def create_school(db: AsyncSession, data: SchoolData) -> School:
        school = School()
        try:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(school, key, value)
            db.add(school)
            await db.commit()
            await db.refresh(school)
            return school
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error occurred: {e}")
            raise ValueError(f"This schoolname already exists: {school.name}")
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"DB error: {e}")
            raise RuntimeError("Database error")
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error: {e}")
            raise

    @staticmethod
    async def delete_school(db: AsyncSession, user: User, school_id: int) -> None:
        school: School = await db.get(School, school_id)
        if school is None:
            logger.warning(
                f"User {user.id} ({user.type}) tried to delete non-existent school ID {school_id}"
            )
            raise NotFound("No such school")

        if user.type == UserTypes.principal:
            principal: Principal = await db.get(Principal, user.id)
            if principal.school_id != school_id:
                logger.warning(
                    f"Principal {user.id} tried to delete school {school_id} not assigned to them"
                )
                raise NotAllowed("Not allowed to delete this school")
        elif user.type != UserTypes.admin:
            logger.warning(
                f"User {user.id} ({user.type}) tried to delete school {school_id} without permission"
            )
            raise NotAllowed("Only admins or assigned principals can delete schools")

        try:
            await db.delete(school)
            await db.commit()
            logger.info(
                f"School ID {school_id} deleted by user {user.id} ({user.type})"
            )
            return None
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"DB error while deleting school {school_id}: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error while deleting school {school_id}: {e}")
            raise

    @staticmethod
    async def update_school_data(db: AsyncSession, school_id: int, data: SchoolUpdate) -> School:
        school: School = await db.get(School, school_id)
        if school is None:
            raise NotFound("No such school")
        try:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(school, key, value)
            await db.commit()
            await db.refresh(school)
            return school
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error occurred: {e}")
            raise ValueError(f'School name "{school.name}" is already taken')
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Unexpected error in DB occurred: {e}")
            raise RuntimeError("Unexpected error in DB")
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def get_school(db: AsyncSession, user: User, school_id: int) -> School:
        try:
            school = await db.get(School, school_id)
            if school is None:
                logger.info(f"School not found id={school_id} by user {user.id}")
                raise NotFound("No such school")

            if user.type == UserTypes.principal:
                principal: Principal = await db.get(Principal, user.id)
                if principal.school_id != school.id:
                    logger.warning(
                        f"Principal {user.id} tried to access school {school.id}"
                    )
                    raise NotAllowed("Cannot access this school")
            elif user.type == UserTypes.teacher:
                teacher: Teacher = await db.get(Teacher, user.id)
                if teacher.school_id != school.id:
                    logger.warning(
                        f"Teacher {user.id} tried to access school {school.id}"
                    )
                    raise NotAllowed("Cannot access this school")
            elif user.type == UserTypes.student:
                student: Student = await db.get(Student, user.id)
                if student.school_id != school.id:
                    logger.warning(
                        f"Student {user.id} tried to access school {school.id}"
                    )
                    raise NotAllowed("Cannot access this school")
            return school
        except Exception as e:
            logger.exception(f"Unexpected error in get_school by user {user.id}: {e}")
            raise

    @staticmethod
    async def get_schools(
        db: AsyncSession, country: str | None = None, is_active: bool | None = None
    ) -> list["School"]:
        try:
            stmt = select(School)

            if country is not None:
                stmt = stmt.where(School.country == country)
            if is_active is not None:
                stmt = stmt.where(School.is_active == is_active)

            result = await db.execute(stmt)
            return result.scalars().all()

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise
