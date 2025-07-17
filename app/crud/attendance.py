from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timezone

from app.db.models.attendance import Attendance
from app.db.models.groups import Group
from app.db.models.types import Teacher, Student
from app.exceptions.attendance import AttendanceNotFound
from app.schemas.attendance import StatusOptions



import logging
logger = logging.getLogger(__name__)

class AttendanceCRUD():
    @staticmethod
    def delete_attendance(db: Session, attendance_id: int):
        try:
            attendance = db.query(attendance).get(attendance_id)
            if not attendance:
                logger.info(f'attendance with id {attendance_id} is not found')
                raise AttendanceNotFound(f'attendance with id {attendance_id} not found')
            db.delete(attendance)
            db.commit()
            logger.info(f'attendance with id {attendance_id} was deleted')
            return attendance
        except SQLAlchemyError as e:
            logger.error(f'Error in db: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise


    @staticmethod
    def get_attendances_id(db: Session, school_id: int | None = None, teacher_id: int | None =  None, group_id: int | None = None, status: StatusOptions | None = None):
        try:
            query = db.query(Attendance)
            if school_id != None:
                students = db.query(Student).filter(Student.school_id == school_id).all()
                ids = [student.id for student in students]
                query = query.filter(Attendance.student_id.in_(ids))
            if teacher_id != None: 
                query = query.filter(Attendance.marked_by == teacher_id)
            if group_id != None:
                students = db.query(Student).filter(Student.group_id == group_id).all()
                ids = [student.id for student in students]
                query = query.filter(Attendance.student_id.in_(ids))
            if status != None:
                query = query.filter(Attendance.status == status)
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f'Error in db: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

    @staticmethod
    def get_attendance_id(db: Session, attendance_id: int):
        try:
            return db.query(Attendance).get(attendance_id)
        except IntegrityError:
            logger.info(f'Attednace not found with if {attendance_id}')
            raise
        except SQLAlchemyError as e:
            logger.error(f'Error in db: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise