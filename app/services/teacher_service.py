from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

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
    def mark_presence(
        db: Session, user: User, student_id: int, lesson_id: int, status: StatusOptions
    ):
        try:
            lesson: Schedule = db.query(Schedule).get(lesson_id)
            student: Student = db.query(Student).get(student_id)
            teacher: Teacher = db.query(Teacher).get(user.id)
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
            if lesson == None:
                logger.info(f"Schedule with id {lesson_id} is not found")
                raise NotFound("Schedule not found")
            if student == None:
                logger.info(f"Student with id {student_id} is not found")
                raise NotFound("Student not found")

            query = db.query(Attendance).filter(Attendance.schedule_id == lesson_id)
            attendance = query.filter(Attendance.student_id == student_id).one_or_none()
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
                    created_at=datetime.now(),
                )
                db.add(attendance)
            db.commit()
            return attendance
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error in dg: {e}")
            raise
        except Exception as e:
            logging.exception(f"Unexpected error occured: {e}")
            raise

    @staticmethod
    def assign_grade(
        db: Session,
        user: User,
        schedule_id: int,
        student_id: int,
        data: AssignGradeData,
    ):
        try:
            student: Student = db.query(Student).get(student_id)
            teacher: Teacher = db.query(Teacher).get(user.id)
            lesson: Schedule = db.query(Schedule).get(schedule_id)
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
            if (
                data.grade_system == GradeSystems.five_num_sys
                and data.value_numeric != None
            ):
                data_dict = data.model_dump(
                    exclude_unset=True,
                    exclude={"value_boolean", "value_str", "value_numeric"},
                )
                data_dict.update({"value_5numerical": data.value_numeric})
            elif (
                data.grade_system == GradeSystems.GPA_sys and data.value_numeric != None
            ):
                data_dict = data.model_dump(
                    exclude_unset=True,
                    exclude={"value_boolean", "value_str", "value_numeric"},
                )
                data_dict.update({"value_GPA": data.value_numeric})
            elif (
                data.grade_system == GradeSystems.percent_sys
                and data.value_numeric != None
            ):
                data_dict = data.model_dump(
                    exclude_unset=True,
                    exclude={"value_boolean", "value_str", "value_numeric"},
                )
                data_dict.update({"value_percent": data.value_numeric})
            elif (
                data.grade_system == GradeSystems.letter_sys
                and data.value_letter != None
            ):
                data_dict = data.model_dump(
                    exclude_unset=True, exclude={"value_boolean", "value_numeric"}
                )
            elif (
                data.grade_system == GradeSystems.pass_fail_sys
                and data.value_boolean != None
            ):
                data_dict = data.model_dump(
                    exclude_unset=True, exclude={"value_numeric", "value_str"}
                )
            else:
                raise NoDataError(
                    "Data is not full:\n"
                    f"Grade system:{data.grade_system} \nvalue_str: {data.value_letter}\nvalue_num: {data.value_numeric}\nvalue_bool: {data.value_boolean}"
                )
            data_dict.update({"student_id": student_id, "schedule_id": schedule_id})
            for key, value in data_dict.items():
                setattr(grade, key, value)

            db.add(grade)
            db.commit()
            db.refresh(grade)
            return grade
        except IntegrityError as e:
            logger.error(f"Integrity error occured: {e}")
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error in db: {e}")
            raise
        except Exception as e:
            logging.exception(f"Unexpected error occured: {e}")
            raise

    @staticmethod
    def accept_invitation(db: Session, user: User, invitation_id: int):
        try:
            invitation: Invitation = db.query(Invitation).get(invitation_id)
            if invitation == None:
                logger.info(f"Invitation with id {invitation_id} not found")
                raise NotFound("Invitation not found")
            if invitation.invited_user_id != user.id:
                raise NotAllowed("Cannot accept another user's invitation")
            logger.info(
                f"User with id {user.id} accepted invitation sent by user with id{invitation.invited_by_id} to school with id {invitation.school_id}"
            )
            invitation.status = Invitation_status.accepted
            teacher: Teacher = db.query(Teacher).get(user.id)
            if teacher == None:
                logger.info(f"Teacher with id {user.id} is not found")
                raise NotFound("Teacher is not found")
            teacher.school_id = invitation.school_id
            db.commit()
            return {"detail": "Invitation accepted"}
        except Exception as e:
            logging.exception(f"Unexpected error occured: {e}")
            raise
