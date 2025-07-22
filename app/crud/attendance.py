from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timezone

from app.db.models.attendance import Attendance
from app.db.models.groups import Group
from app.db.models.types import Teacher, Student, Principal
from app.db.models.users import User
from app.db.models.schedules import Schedule
from app.exceptions.attendance import AttendanceNotFound
from app.exceptions.basic import NotAllowed, NotFound
from app.schemas.attendance import StatusOptions
from app.schemas.users import UserTypes



import logging
logger = logging.getLogger(__name__)

class AttendanceCRUD():
    @staticmethod
    def delete_attendance(db: Session, user: User ,attendance_id: int):
        try:
            attendance: Attendance = db.query(Attendance).get(attendance_id)
            schedule: Schedule = db.query(Schedule).get(attendance.schedule_id)
            if not attendance:
                logger.info(f'attendance with id {attendance_id} is not found')
                raise NotFound(f'attendance with id {attendance_id} not found')
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if principal.school_id != schedule.school_id:
                    logger.warning(f'User with id {user.id} tried to delete attendance with id {attendance_id}, but from another school')
                    raise NotAllowed('Cannot delete from other schools')
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
    def get_attendances_id(db: Session, user: User , school_id: int , teacher_id: int | None =  None, group_id: int | None = None, status: StatusOptions | None = None):
        try: 
            query = db.query(Attendance)
            if user.type == UserTypes.teacher:
                user_role: Teacher = db.query(Teacher).get(user.id)
            elif user.type == UserTypes.student:
                user_role: Student = db.query(Student).get(user.id)
            elif user.type == UserTypes.principal:
                user_role: Principal = db.query(Principal).get(user.id)

            if user.type != UserTypes.admin: 
                if user_role.school_id != school_id:
                    logger.warning(f'User with id {user.id} from school wit id {user_role.school_id} tried to access data from school with id {school_id}. Not allowed')
                    raise NotAllowed('Cannot get attendance from other schools')
                students = db.query(Student).filter(Student.school_id == school_id).all()
                ids = [student.id for student in students]
                query = query.filter(Attendance.student_id.in_(ids))
            else:
                students = db.query(Student).filter(Student.school_id == school_id).all()
                ids = [student.id for student in students]
                query = query.filter(Attendance.student_id.in_(ids))

            if teacher_id != None:
                query = query.filter(Attendance.marked_by == teacher_id)

            if group_id != None:
                students = db.query(Student).filter(Student.school_id == school_id , Student.group_id == group_id).all()
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
    def get_attendance_id(db: Session, user: User ,attendance_id: int):
        try:
            attendance: Attendance = db.query(Attendance).get(attendance_id)
            schedule: Schedule = db.query(Schedule).get(attendance.schedule_id)
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if principal.school_id != schedule.school_id:
                    logger.warning('User with id {user.id} tried to access attendance with id {attendance_id}. Not allowed to access other schools')
                    raise NotAllowed('Cannot access other schools')
            elif user.type == UserTypes.teacher:
                teacher: Teacher = db.query(Teacher).get(user.id)
                if attendance.marked_by != teacher.id:
                    logger.warning('User with id {user.id} tried to access attendance with id {attendance_id}. Not allowed to access other schools')
                    raise NotAllowed('Cannot access attendance from other teachers or schools')              
            elif user.type == UserTypes.student:
                student: Student = db.query(Student).get(user.id)
                if attendance.student_id != student.id:
                    raise NotAllowed('Cannot access attendance for other students or schools')
            return attendance
        except IntegrityError:
            logger.info(f'Attednace not found with if {attendance_id}')
            raise
        except SQLAlchemyError as e:
            logger.error(f'Error in db: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

