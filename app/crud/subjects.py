from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.future import select

from app.db.models.subjects import Subject
from app.db.models.users import User
from app.db.models.types import Teacher, Student, Principal
from app.schemas.subjects import SubjectData, SubjectUpdate
from app.exceptions.basic import NotFound, NotAllowed
from app.schemas.auth import UserTypes

import logging

logger = logging.getLogger(__name__)


class SubjectCRUD:
    @staticmethod
    async def create_subject(db: AsyncSession, data: SubjectData) -> Subject:
        try:
            subject = Subject()
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(subject, key, value)
            db.add(subject)
            await db.commit()
            await db.refresh(subject)
            return subject
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error occurred: {e}")
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Error in DB: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def delete_subject(db: AsyncSession, user: User, subject_id: int):
        try:
            subject: Subject = await db.get(Subject, subject_id)
            if not subject:
                logger.info(f"Subject with id {subject_id} not found")
                raise NotFound(f"Subject with id {subject_id} not found")

            if user.type == UserTypes.principal:
                principal: Principal = await db.get(Principal, user.id)
                if principal.school_id != subject.school_id:
                    logger.warning(
                        f"User {user.id} tried to delete subject {subject_id} from another school"
                    )
                    raise NotAllowed("Cannot delete subjects from other schools")

            await db.delete(subject)
            await db.commit()
            logger.info(f"Subject with id {subject_id} was deleted")
            return True
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"DB error: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def update_subject_data(
        db: AsyncSession, subject_id: int, data: SubjectUpdate
    ):
        subject: Subject = await db.get(Subject, subject_id)
        if not subject:
            logger.info(f"Subject with id {subject_id} not found")
            raise NotFound("No such subject")
        try:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(subject, key, value)
            await db.commit()
            await db.refresh(subject)
            return subject
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error occurred: {e}")
            raise ValueError(f'Subject name "{subject.name}" is already taken')
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Unexpected DB error occurred: {e}")
            raise RuntimeError("Unexpected error in DB")
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def get_subject_id(db: AsyncSession, user: User, subject_id: int):
        try:
            subject: Subject = await db.get(Subject, subject_id)
            if not subject:
                raise NotFound(f"Subject with id {subject_id} not found")

            if user.type == UserTypes.principal:
                principal: Principal = await db.get(Principal, user.id)
                if principal.school_id != subject.school_id:
                    raise NotAllowed("Cannot access subjects from other schools")
            elif user.type == UserTypes.teacher:
                teacher: Teacher = await db.get(Teacher, user.id)
                if teacher.school_id != subject.school_id:
                    raise NotAllowed("Cannot access subjects from other schools")
            elif user.type == UserTypes.student:
                student: Student = await db.get(Student, user.id)
                if student.school_id != subject.school_id:
                    raise NotAllowed("Cannot access subjects from other schools")

            return subject
        except SQLAlchemyError as e:
            logger.error(f"DB error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def get_subjects(
        db: AsyncSession, user: User, school_id: int, name: str | None = None
    ):
        try:
            if user.type == UserTypes.teacher:
                teacher: Teacher = await db.get(Teacher, user.id)
                if teacher.school_id != school_id:
                    raise NotAllowed("Cannot get subjects from other schools")
            elif user.type == UserTypes.student:
                student: Student = await db.get(Student, user.id)
                if student.school_id != school_id:
                    raise NotAllowed("Cannot get subjects from other schools")
            elif user.type == UserTypes.principal:
                principal: Principal = await db.get(Principal, user.id)
                if principal.school_id != school_id:
                    raise NotAllowed("Cannot get subjects from other schools")

            stmt = select(Subject).filter(Subject.school_id == school_id)
            if name:
                stmt = stmt.filter(Subject.name == name)
            result = await db.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"DB error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            raise
