from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timezone

from app.db.models.schedules import Schedule
from app.db.models.types import Student, Teacher
from app.db.models.attendance import Attendance
from app.db.models.grades import Grade
from app.exceptions.basic import NoDataError, NotFound, NotAllowed
from app.schemas.attendance import StatusOptions
from app.schemas.grades import AssignGradeData, GradeSystems
from app.schemas.invitations import Invitation_status
from app.schemas.users import UserTypes
from app.db.models.users import User
from app.db.models.invitations import Invitation

import logging

logger = logging.getLogger(__name__)


class TeacherService:
    @staticmethod
    async def mark_presence(
        db: AsyncSession,
        user: User,
        student_id: int,
        lesson_id: int,
        status: StatusOptions,
    ):
        try:
            lesson: Schedule | None = await db.get(Schedule, lesson_id)
            student: Student | None = await db.get(Student, student_id)
            teacher: Teacher | None = await db.get(Teacher, user.id)

            if lesson is None:
                logger.info(f"Schedule with id {lesson_id} is not found")
                raise NotFound("Schedule not found")
            if student is None:
                logger.info(f"Student with id {student_id} is not found")
                raise NotFound("Student not found")

            if teacher.school_id != student.school_id:
                logger.warning(
                    f"User with id {user.id} tried to access school with id {student.school_id}"
                )
                raise NotAllowed("Cannot access other schools")
            if teacher.school_id != lesson.school_id:
                logger.warning(
                    f"User with id {user.id} tried to access school with id {lesson.school_id}"
                )
                raise NotAllowed("Cannot access other schools")

            # check existing attendance
            result = await db.execute(
                select(Attendance).where(
                    Attendance.schedule_id == lesson_id,
                    Attendance.student_id == student_id,
                )
            )
            attendance: Attendance | None = result.scalar_one_or_none()

            if attendance:
                attendance.status = status
                attendance.updated_at = datetime.now(tz=timezone.utc)
                attendance.marked_by = user.id
            else:
                attendance = Attendance(
                    status=True,
                    student_id=student_id,
                    marked_by=teacher.id,
                    schedule_id=lesson_id,
                    created_at=datetime.now(tz=timezone.utc),
                )
                db.add(attendance)

            await db.commit()
            await db.refresh(attendance)
            return attendance

        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Error in db: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def assign_grade(
        db: AsyncSession,
        user: User,
        schedule_id: int,
        student_id: int,
        data: AssignGradeData,
    ):
        try:
            student: Student | None = await db.get(Student, student_id)
            teacher: Teacher | None = await db.get(Teacher, user.id)
            lesson: Schedule | None = await db.get(Schedule, schedule_id)

            if student is None:
                raise NotFound("Student not found")
            if lesson is None:
                raise NotFound("Schedule not found")

            if user.type != UserTypes.admin:
                if teacher.school_id != student.school_id:
                    logger.warning(
                        f"User with id {user.id} tried to access school with id {student.school_id}"
                    )
                    raise NotAllowed("Cannot access other schools")
                if teacher.school_id != lesson.school_id:
                    logger.warning(
                        f"User with id {user.id} tried to access school with id {lesson.school_id}"
                    )
                    raise NotAllowed("Cannot access other schools")

            grade = Grade()

            match (
                data.grade_system,
                data.value_numeric,
                data.value_letter,
                data.value_boolean,
            ):
                case (GradeSystems.five_num_sys, numeric, None, None) if (
                    numeric is not None
                ):
                    data_dict = data.model_dump(
                        exclude_unset=True,
                        exclude={"value_boolean", "value_str", "value_numeric"},
                    )
                    data_dict.update({"value_5numerical": numeric})

                case (GradeSystems.GPA_sys, numeric, None, None) if numeric is not None:
                    data_dict = data.model_dump(
                        exclude_unset=True,
                        exclude={"value_boolean", "value_str", "value_numeric"},
                    )
                    data_dict.update({"value_GPA": numeric})

                case (GradeSystems.percent_sys, numeric, None, None) if (
                    numeric is not None
                ):
                    data_dict = data.model_dump(
                        exclude_unset=True,
                        exclude={"value_boolean", "value_str", "value_numeric"},
                    )
                    data_dict.update({"value_percent": numeric})

                case (GradeSystems.letter_sys, None, letter, None) if (
                    letter is not None
                ):
                    data_dict = data.model_dump(
                        exclude_unset=True, exclude={"value_boolean", "value_numeric"}
                    )

                case (GradeSystems.pass_fail_sys, None, None, boolean) if (
                    boolean is not None
                ):
                    data_dict = data.model_dump(
                        exclude_unset=True, exclude={"value_numeric", "value_str"}
                    )

                case _:
                    raise NoDataError(
                        "Data is not full:\n"
                        f"Grade system:{data.grade_system} \n"
                        f"value_str: {data.value_letter}\n"
                        f"value_num: {data.value_numeric}\n"
                        f"value_bool: {data.value_boolean}"
                    )

            data_dict.update({"student_id": student_id, "schedule_id": schedule_id})
            for key, value in data_dict.items():
                setattr(grade, key, value)

            db.add(grade)
            await db.commit()
            await db.refresh(grade)
            return grade

        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error occurred: {e}")
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Error in db: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def accept_invitation(db: AsyncSession, user: User, invitation_id: int):
        try:
            invitation: Invitation | None = await db.get(Invitation, invitation_id)
            if invitation is None:
                logger.info(f"Invitation with id {invitation_id} not found")
                raise NotFound("Invitation not found")

            if invitation.invited_user_id != user.id:
                raise NotAllowed("Cannot accept another user's invitation")

            logger.info(
                f"User with id {user.id} accepted invitation sent by user with id {invitation.invited_by_id} "
                f"to school with id {invitation.school_id}"
            )

            invitation.status = Invitation_status.accepted

            teacher: Teacher | None = await db.get(Teacher, user.id)
            if teacher is None:
                logger.info(f"Teacher with id {user.id} is not found")
                raise NotFound("Teacher is not found")

            teacher.school_id = invitation.school_id
            await db.commit()

            return {"detail": "Invitation accepted"}

        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise
