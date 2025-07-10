from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from datetime import datetime, date, timezone


from app.schemas.schedules import ScheduleData, ScheduleUpdateData
from app.exceptions.schedules import ScheduleNotFound
from app.exceptions.subject import SubjectNotFound
from app.exceptions.teachers import TeacherNotFound
from app.exceptions.school import SchoolNotFound
from app.exceptions.groups import GroupNotFound
from app.db.models.types import Student, Teacher
from app.db.models.schedules import Schedule
from app.db.models.attendance import Attendance
from app.db.models.groups import Group
from app.db.models.schools import School
from app.db.models.subjects import Subject

import logging
logger = logging.getLogger(__name__)

def create_attendance(db: Session, schedules: list[Schedule], school_id: int | None = None, group_id: int | None = None):
    today = date.today()
    attendances = []
    if group_id:
        students = db.query(Student).filter(Student.group_id == group_id)
    if school_id:     
        students = db.query(Student).filter(Student.school_id == school_id)
    for schedule in schedules:
        for student in students:
            query = db.query(Attendance).filter(Attendance.schedule_id == schedule.id)
            query = query.filter(Attendance.student_id == student.id)
            query = query.filter(Attendance.created_at == today).first()
            if query:
                continue
            attendance = Attendance(schedule_id = schedule.id, student_id = student.id, created_at = today)
            db.add(attendance)
            db.commit()
            db.refresh(attendance)
            attendances.append(attendance)
    return attendances



class ScheduleCRUD():
    @staticmethod
    def create_schedule(db: Session, data: ScheduleData):
        try:
            subject = db.query(Subject).get(data.subject_id)
            teacher = db.query(Teacher).get(data.teacher_id)
            group = db.query(Group).get(data.group_id)
            school = db.query(School).get(data.school_id)
            if not subject:
                raise SubjectNotFound('Subject not found')
            if not teacher:
                raise TeacherNotFound('Teacher not found')
            if not group:
                raise GroupNotFound('Group not found')
            if not school:
                raise SchoolNotFound('School not found')

            data_dict = data.model_dump(exclude_unset=True)
            schedule = Schedule(** data_dict, created_at = datetime.now(tz=timezone.utc))
            db.add(schedule)
            db.commit()
            db.refresh(schedule)
            return schedule
        except IntegrityError as e:
            logger.error(f'Integrity error occured: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

    @staticmethod
    def get_schedule_id(db: Session, schedule_id: int):
        try: 
            schedule = db.query(Schedule).get(schedule_id)
            if not schedule:
                raise ScheduleNotFound('Schedule not found')
            return schedule
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

    @staticmethod
    def get_schedule_today(db: Session, school_id: int | None = None, group_id: int | None = None, teacher_id: int | None = None):
        try:
            today_of_week = date.today().strftime('%A').lower()
            query = db.query(Schedule).filter(Schedule.day_of_week == today_of_week)
            if school_id:
                query = query.filter(Schedule.school_id == school_id)
            if group_id:
                query = query.filter(Schedule.group_id == group_id)
            if teacher_id:
                query = query.filter(Schedule.teacher_id == teacher_id)
            create_attendance(db=db, schedules=query.all(), school_id=school_id, group_id=group_id)
            return query.all() 
        except Exception as e:
            logger.exception(f'Unexpected error occurred: {e}')
            raise
    
    @staticmethod
    def delete_schedule(db: Session, schedule_id: int):
        try:
            schedule = db.query(Schedule).get(schedule_id)
            db.delete(schedule)
            db.commit()
        except Exception as e:
            logger.exception(f'Unexpected error occurred: {e}')
            raise
    
    @staticmethod
    def update_schedule(db: Session, schedule_id: int , data: ScheduleUpdateData):
        try:
            data_dict = data.model_dump(exclude_unset=True)
            schedule = db.query(Schedule).get(schedule_id)
            for key, value in data_dict.items():
                setattr(schedule, key, value) 
            db.add(schedule)
            db.commit()
            db.refresh(schedule)
        except IntegrityError as e:
            logger.error(f'Integrity error occured: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise