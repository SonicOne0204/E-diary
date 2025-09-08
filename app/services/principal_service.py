from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.db.models.groups import Group
from app.db.models.types import Teacher, Student, Principal
from app.db.models.users import User
from app.db.models.subjects import Subject
from app.db.models.associations import subject_teacher
from app.db.models.invitations import Invitation
from app.exceptions.teachers import TeacherAlreadyAssigned, TeacherNotInTable
from app.exceptions.students import StudentAlreadyAssigned, StudentNotInTable
from app.exceptions.basic import NotFound, NotAllowed

import logging

logger = logging.getLogger(__name__)


class PrincipalService:
    @staticmethod
    async def invite_teacher_to_school_id(
        db: AsyncSession, user: User, school_id: int, teacher_id: int
    ) -> Invitation:
        try:
            userside_teacher: User | None = await db.get(User, teacher_id)
            if userside_teacher is None:
                logger.info(f"Teacher with id {teacher_id} is not found")
                raise NotFound("Teacher not found")
            if userside_teacher.type != "teacher":
                logger.warning(f"User with id {teacher_id} has type not 'teacher'")
                raise NotFound(f"This user is {userside_teacher.type}, not teacher")

            result = await db.execute(
                select(Teacher).where(Teacher.id == userside_teacher.id)
            )
            teacher: Teacher | None = result.scalar_one_or_none()
            if teacher is None:
                raise TeacherNotInTable(teacher_id=userside_teacher.id)
            if teacher.school_id is not None:
                raise TeacherAlreadyAssigned(
                    teacher_id=teacher.id, school_id=teacher.school_id
                )

            invitation = Invitation(
                school_id=school_id, invited_by_id=user.id, invited_user_id=teacher.id
            )
            db.add(invitation)
            await db.commit()
            await db.refresh(invitation)
            return invitation

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error in DB: {e}")
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"SQLAlchemy error in DB: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def invite_student_to_school_id(
        db: AsyncSession, user: User, school_id: int, student_id: int
    ) -> Invitation:
        try:
            userside_student: User | None = await db.get(User, student_id)
            if userside_student is None:
                logger.info(f"Student with id {student_id} is not found")
                raise NotFound("Student not found")
            if userside_student.type != "student":
                logger.warning(f"User with id {student_id} has type not 'student'")
                raise NotFound(f"This user is {userside_student.type}, not student")

            result = await db.execute(
                select(Student).where(Student.id == userside_student.id)
            )
            student: Student | None = result.scalar_one_or_none()
            if student is None:
                raise StudentNotInTable(student_id=userside_student.id)
            if student.school_id is not None:
                raise StudentAlreadyAssigned(
                    student_id=student.id, school_id=student.school_id
                )

            invitation = Invitation(
                school_id=school_id, invited_by_id=user.id, invited_user_id=student.id
            )
            db.add(invitation)
            await db.commit()
            await db.refresh(invitation)
            return invitation

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error in DB: {e}")
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"SQLAlchemy error in DB: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def link_student_to_group_id(
        db: AsyncSession, user: User, group_id: int, student_id: int
    ) -> Student:
        try:
            userside_student: User | None = await db.get(User, student_id)
            if userside_student is None or userside_student.type != "student":
                raise NotFound("Student not found")

            student: Student | None = await db.get(Student, userside_student.id)
            principal: Principal | None = await db.get(Principal, user.id)
            group: Group | None = await db.get(Group, group_id)

            if student is None:
                raise StudentNotInTable(student_id=userside_student.id)
            if student.group_id is not None:
                raise StudentAlreadyAssigned(
                    student_id=student.id, group_id=student.group_id
                )
            if student.school_id != principal.school_id:
                raise NotAllowed("Cannot assign students from other schools")
            if group.school_id != principal.school_id:
                raise NotAllowed("Cannot assign groups from other schools")

            student.group_id = group_id
            await db.commit()
            await db.refresh(student)
            return student

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error in DB: {e}")
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"SQLAlchemy error in DB: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def link_teacher_to_subject_id(
        db: AsyncSession, user: User, teacher_id: int, subject_id: int
    ):
        try:
            subject: Subject | None = await db.get(Subject, subject_id)
            teacher: User | None = await db.get(User, teacher_id)
            principal: Principal | None = await db.get(Principal, user.id)

            if teacher is None:
                raise NotFound("User not found")
            if teacher.type != "teacher":
                raise NotFound("User is not teacher")
            if subject is None:
                raise NotFound("Subject not found")
            if teacher.school_id != principal.school_id:
                raise NotAllowed("Cannot assign teachers from other schools")
            if subject.school_id != principal.school_id:
                raise NotAllowed("Cannot assign subjects from other schools")

            await db.execute(
                subject_teacher.insert().values(
                    teacher_id=teacher.id, subject_id=subject.id
                )
            )
            await db.commit()

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"SQLAlchemy error in DB: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise
