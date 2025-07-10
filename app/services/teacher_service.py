from sqlalchemy.orm import Session
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.db.models.schedules import Schedule
from app.db.models.types import Student, Teacher
from app.db.models.attendance import Attendance
from app.db.models.grades import Grade
from app.exceptions.schedules import ScheduleNotFound
from app.exceptions.students import StudentNotFound
from app.exceptions.basic import NoDataError
from app.exceptions.teachers import TeacherNotFound
from app.schemas.attendance import StatusOptions
from app.schemas.grades import AssignGradeData, GradeSystems


import logging
logger = logging.getLogger(__name__)


class TeacherService():
    @staticmethod
    def mark_presence(db: Session, student_id: int, lesson_id: int, status: StatusOptions, teacher_id: int | None = None ):
        try:
            lesson = db.query(Schedule).get(lesson_id)
            student = db.query(Student).get(student_id)
            teacher = db.query(Teacher).get(teacher_id)
            if lesson == None:
                raise ScheduleNotFound('Schedule not found')
            if student == None:
                raise StudentNotFound('Student not found')
            if teacher == None:
                raise TeacherNotFound('Teacher not found')
            
            query = db.query(Attendance).filter(Attendance.schedule_id == lesson_id)
            attendance = query.filter(Attendance.student_id == student_id).one_or_none()
            if attendance:
                attendance.status = status
                attendance.updated_at = datetime.now(tz=timezone.utc)
                attendance.marked_by = teacher_id
            else:
                if teacher_id != None:
                    attendance = Attendance(status=True, student_id=student_id, marked_by=teacher_id, schedule_id=lesson_id, created_at=datetime.now())
                else:
                    attendance = Attendance(status=True, student_id=student_id, schedule_id=lesson_id, created_at=datetime.now())
                db.add(attendance)
            db.commit()
            return attendance
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error in dg: {e}')
            raise
        except Exception as e:
            logging.exception(f'Unexpected error occured: {e}')
            raise
    @staticmethod
    def assign_grade(db: Session, data: AssignGradeData):
        try:
            grade = Grade()
            if data.grade_system == GradeSystems.five_num_sys and data.value_numeric != None:
                data_dict = data.model_dump(exclude_unset=True, exclude={'value_boolean', 'value_str', 'value_numeric'})
                data_dict.update({'value_5numerical': data.value_numeric})
            elif data.grade_system == GradeSystems.GPA_sys and data.value_numeric != None:
                data_dict = data.model_dump(exclude_unset=True, exclude={'value_boolean', 'value_str', 'value_numeric'})
                data_dict.update({'value_GPA': data.value_numeric})
            elif data.grade_system == GradeSystems.percent_sys and data.value_numeric != None:
                data_dict = data.model_dump(exclude_unset=True, exclude={'value_boolean', 'value_str', 'value_numeric'})
                data_dict.update({'value_percent': data.value_numeric})
            elif data.grade_system == GradeSystems.letter_sys and data.value_letter != None:
                data_dict = data.model_dump(exclude_unset=True, exclude={'value_boolean', 'value_numeric'})
            elif data.grade_system == GradeSystems.pass_fail_sys and data.value_boolean != None:
                data_dict = data.model_dump(exclude_unset=True, exclude={'value_numeric', 'value_str'})
            else:
                raise NoDataError(
                'Data is not full:\n'
                f'Grade system:{data.grade_system} \n'
                f'value_str: {data.value_letter}\n'
                f'value_num: {data.value_numeric}\n'
                f'value_bool: {data.value_boolean}'
                )
            for key,value in data_dict.items():
                setattr(grade, key, value)
            db.add(grade)
            db.commit()
            db.refresh(grade)
            return grade
        except IntegrityError as e:
            logger.error(f'Integrity error occured: {e}')
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error in dg: {e}')
            raise
        except Exception as e:
            logging.exception(f'Unexpected error occured: {e}')
            raise
            