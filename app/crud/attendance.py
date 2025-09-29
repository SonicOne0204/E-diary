from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.attendance import Attendance
from app.db.models.types import Teacher, Student, Principal
from app.db.models.users import User
from app.db.models.schedules import Schedule
from app.exceptions.basic import NotAllowed, NotFound
from app.schemas.attendance import StatusOptions
from app.schemas.users import UserTypes

import logging

logger = logging.getLogger(__name__)


class AttendanceCRUD:
    @staticmethod
    async def delete_attendance(db: AsyncSession, user: User, attendance_id: int):
        try:
            attendance: Attendance = await db.get(Attendance, attendance_id)
            if not attendance:
                logger.info(f"attendance with id {attendance_id} is not found")
                raise NotFound(f"attendance with id {attendance_id} not found")

            schedule: Schedule = await db.get(Schedule, attendance.schedule_id)

            if user.type == UserTypes.principal:
                principal: Principal = await db.get(Principal, user.id)
                if principal.school_id != schedule.school_id:
                    logger.warning(
                        f"User with id {user.id} tried to delete attendance with id {attendance_id}, but from another school"
                    )
                    raise NotAllowed("Cannot delete from other schools")

            await db.delete(attendance)
            await db.commit()
            logger.info(f"attendance with id {attendance_id} was deleted")
            return attendance
        except SQLAlchemyError as e:
            logger.error(f"Error in db: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def get_attendances_id(
        db: AsyncSession,
        user: User,
        school_id: int,
        teacher_id: int | None = None,
        group_id: int | None = None,
        status: StatusOptions | None = None,
    ):
        try:
            query = select(Attendance)

            # Get user type instance
            if user.type == UserTypes.teacher:
                user_type: Teacher = await db.get(Teacher, user.id)
            elif user.type == UserTypes.student:
                user_type: Student = await db.get(Student, user.id)
            elif user.type == UserTypes.principal:
                user_type: Principal = await db.get(Principal, user.id)

            # Non-admin users restricted to their school
            if user.type != UserTypes.admin:
                if user_type.school_id != school_id:
                    logger.warning(
                        f"User {user.id} from school {user_type.school_id} tried to access data from school {school_id}. Not allowed"
                    )
                    raise NotAllowed("Cannot get attendance from other schools")

                # Get students in the school
                result = await db.execute(
                    select(Student).where(Student.school_id == school_id)
                )
                students = result.scalars().all()
                ids = [student.id for student in students]
                query = query.where(Attendance.student_id.in_(ids))
            else:
                # Admin: optional filtering by school
                result = await db.execute(
                    select(Student).where(Student.school_id == school_id)
                )
                students = result.scalars().all()
                ids = [student.id for student in students]
                query = query.where(Attendance.student_id.in_(ids))

            if teacher_id is not None:
                query = query.where(Attendance.marked_by == teacher_id)

            if group_id is not None:
                result = await db.execute(
                    select(Student).where(
                        Student.school_id == school_id, Student.group_id == group_id
                    )
                )
                students = result.scalars().all()
                ids = [student.id for student in students]
                query = query.where(Attendance.student_id.in_(ids))

            if status is not None:
                query = query.where(Attendance.status == status)

            result = await db.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error in db: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def get_attendance_id(db: AsyncSession, user: User, attendance_id: int):
        try:
            attendance: Attendance = await db.get(Attendance, attendance_id)
            if not attendance:
                raise NotFound(f"Attendance {attendance_id} not found")

            schedule: Schedule = await db.get(Schedule, attendance.schedule_id)

            if user.type == UserTypes.principal:
                principal: Principal = await db.get(Principal, user.id)
                if principal.school_id != schedule.school_id:
                    logger.warning(
                        f"User {user.id} tried to access attendance {attendance_id}. Not allowed"
                    )
                    raise NotAllowed("Cannot access other schools")
            elif user.type == UserTypes.teacher:
                teacher: Teacher = await db.get(Teacher, user.id)
                if attendance.marked_by != teacher.id:
                    logger.warning(
                        f"User {user.id} tried to access attendance {attendance_id}. Not allowed"
                    )
                    raise NotAllowed(
                        "Cannot access attendance from other teachers or schools"
                    )
            elif user.type == UserTypes.student:
                student: Student = await db.get(Student, user.id)
                if attendance.student_id != student.id:
                    raise NotAllowed(
                        "Cannot access attendance for other students or schools"
                    )

            return attendance
        except SQLAlchemyError as e:
            logger.error(f"Error in db: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            raise
