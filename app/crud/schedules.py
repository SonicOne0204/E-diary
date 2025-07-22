from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fastapi import Depends
from typing import Annotated
from datetime import datetime, date, timezone


from app.schemas.schedules import ScheduleData, ScheduleUpdateData
from app.schemas.users import UserTypes
from app.exceptions.basic import NotAllowed, NotFound
from app.db.models.types import Student, Teacher
from app.db.models.schedules import Schedule
from app.db.models.attendance import Attendance
from app.db.models.groups import Group
from app.db.models.schools import School
from app.db.models.subjects import Subject
from app.db.models.users import User
from app.db.models.types import Principal
from app.services.auth import get_current_user

import logging
logger = logging.getLogger(__name__)

def create_attendance(db: Session, schedules: list[Schedule], school_id: int | None = None, group_id: int | None = None):
    try:
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
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise



class ScheduleCRUD():
    @staticmethod
    def create_schedule(db: Session, data: ScheduleData, user: Annotated[User, Depends(get_current_user)]):
        try:
            subject: Subject = db.query(Subject).get(data.subject_id)
            teacher: Teacher = db.query(Teacher).get(data.teacher_id)
            group: Group = db.query(Group).get(data.group_id)
            school: School = db.query(School).get(data.school_id)
            principal: Principal = db.query(Principal).get(user.id)
            if not subject:
                logger.info(f'Subject with id {data.subject_id} not found')
                raise NotFound('Subject not found')
            if not teacher:
                logger.info(f'Teacher with id {data.teacher_id} not found')
                raise NotFound('Teacher not found')
            if not group:
                logger.info(f'Group with id {data.group_id} not found')
                raise NotFound('Group not found')
            if not school:
                logger.info(f'School with id {data.school_id} not found')
                raise NotFound('School not found')
            if data.school_id != principal.school_id and user.type == UserTypes.principal:
                logger.warning(f'Principal with id {principal.id} cannot asign schedule to school {school.id}')
                raise NotAllowed('Cannot asign schedule to another school')
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
            schedule: Schedule = db.query(Schedule).get(schedule_id)
            if not schedule:
                logger.info(f'schedule with id {schedule_id} not found')
                raise NotFound('Schedule not found')
            return schedule
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

    @staticmethod
    def get_schedule_today(db: Session, user: User, school_id: int | None = None, group_id: int | None = None, teacher_id: int | None = None):
        try:
            today_of_week = date.today().strftime('%A').lower()
            query = db.query(Schedule).filter(Schedule.day_of_week == today_of_week)
            match user.type:
                case UserTypes.principal:
                    principal: Principal = db.query(Principal).get(user.id)
                    user_school_id = principal.school_id
                case UserTypes.teacher:
                    teacher: Teacher = db.query(Teacher).get(user.id)
                    user_school_id = teacher.school_id
                case UserTypes.student:
                    student: Student = db.query(Student).get(user.id)
                    user_school_id = student.school_id
            if school_id != None:
                if user.type != UserTypes.admin:
                    logger.warning(f'principal with id {user.id} tried to access school with id {school_id} but {user.type} is not allowed')
                    raise NotAllowed(f'{user.type} cannot access other schools')
                query = query.filter(Schedule.school_id == school_id)
            else:
                query = query.filter(Schedule.school_id == user_school_id)
            if group_id:
                query = query.filter(Schedule.group_id == group_id)
            if teacher_id:
                query = query.filter(Schedule.teacher_id == teacher_id)
            if user_school_id:
                create_attendance(db=db, schedules=query.all(), school_id=user_school_id, group_id=group_id)
            else:
                create_attendance(db=db, schedules=query.all(), school_id=school_id, group_id=group_id)
            return query.all() 
        except Exception as e:
            logger.exception(f'Unexpected error occurred: {e}')
            raise
    
    @staticmethod
    def delete_schedule(db: Session, user: User,  schedule_id: int):
        try:
            schedule: Schedule = db.query(Schedule).get(schedule_id)
            if not schedule:
                logger.info(f'schedule with id {schedule_id} not found')
                raise NotFound('Schedule not found')
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if schedule.school_id != principal.school_id:
                    logger.warning(f'Principal with id {user.id} cannot delete schedule with id {schedule.id} from school with id {schedule.school_id}')
                    raise NotAllowed(f'Principal cannot delete schedule from other schools')
            db.delete(schedule)
            db.commit()
        except Exception as e:
            logger.exception(f'Unexpected error occurred: {e}')
            raise
    
    @staticmethod
    def update_schedule(db: Session, user: User ,schedule_id: int , data: ScheduleUpdateData):
        try:
            schedule: Schedule = db.query(Schedule).get(schedule_id)
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if schedule.school_id != principal.school_id:
                    logger.warning(f'Principal with id {user.id} cannot update from schedule with id {schedule.school_id}')
                    raise NotAllowed(f'Principal cannot update schedule from other schools')
            data_dict = data.model_dump(exclude_unset=True)
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