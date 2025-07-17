from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timezone

from app.schemas.homeworks import HomeworkData, HomeworkDataUpdate
from app.db.models.homeworks import Homework
from app.db.models.groups import Group
from app.db.models.types import Teacher

from app.exceptions.basic import NotAllowed, NotFound


import logging
logger = logging.getLogger(__name__)

class HomeworkCRUD():
    @staticmethod
    def add_homework(db: Session, data: HomeworkData):
        try:
            group: Group = db.query(Group).get(data.group_id)
            teacher: Teacher = db.query(Teacher).get(data.teacher_id)
            if group.school_id != data.school_id:
                logger.warning(f'Access denied while creating homework. Group with id {group.id} is assigned to school with id {group.school_id}. Not allowed to give homework')
                raise NotAllowed(f'Group with id {group.id} is assigned to school with id {group.school_id}. Not allowed to give homework')
            if teacher.school_id != data.school_id:
                logger.warning(f'Access denied while creating homework. Teacher with id {teacher.id} is assigned to school with id {teacher.school_id}. Not allowed to give homework')
                raise NotAllowed(f'Teacher with id {teacher.id} is assinged to school with id {teacher.school_id}. Not allowed to give homework')
            homework = Homework()
            data_dict = data.model_dump(exclude={'due_date'})
            if isinstance(data.due_date, str):
                parsed_dt = datetime.fromisoformat(data.due_date)
            else:
                parsed_dt = data.due_date
            homework.due_date = parsed_dt.replace(second=0, microsecond=0)
            for key, value in data_dict.items():
                setattr(homework, key, value)
            db.add(homework)
            db.commit()
            db.refresh(homework)
            return homework
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error in db occured: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

    @staticmethod
    def delete_homework(db: Session, homework_id: int):
        try:
            homework = db.query(Homework).get(homework_id)
            if not homework:
                logger.info(f'Homework with id {homework_id} is not found')
                raise NotFound(f'Homework with id {homework_id} not found')
            db.delete(homework)
            db.commit()
            logger.info(f'Homework with id {homework_id} was deleted')
            return homework
        except SQLAlchemyError as e:
            logger.error(f'Error in db: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

    @staticmethod
    def update_homework(db: Session, homework_id: int, data: HomeworkDataUpdate):
        try:
            homework: Homework = db.query(Homework).get(homework_id)
            if not homework:
                raise NotFound('Homework not found')
            group: Group = db.query(Group).get(data.group_id)
            teacher: Teacher = db.query(Teacher).get(data.teacher_id)
            if group.school_id != homework.school_id:
                logger.warning(f'Access denied while creating homework. Group with id {group.id} is assigned to school with id {group.school_id}. Not allowed to give homework')
                raise NotAllowed(f'Group with id {group.id} is assigned to school with id {group.school_id}. Not allowed to give homework')
            if teacher.school_id != homework.school_id:
                logger.warning(f'Access denied while creating homework. Teacher with id {teacher.id} is assigned to school with id {teacher.school_id}. Not allowed to give homework')
                raise NotAllowed(f'Teacher with id {teacher.id} is assinged to school with id {teacher.school_id}. Not allowed to give homework')
            data_dict = data.model_dump(exclude={'due_date'})
            if isinstance(data.due_date, str):
                parsed_dt = datetime.fromisoformat(data.due_date)
            else:
                parsed_dt = data.due_date
            homework.due_date = parsed_dt.replace(microsecond=0, second=0)
            for key, value in data_dict.items():
                setattr(homework, key, value)
            db.add(homework)
            db.commit()
            db.refresh(homework)
            return homework
        except IntegrityError as e:
            logger.error(f'Integrity error occured: {e}')
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error in db occured: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

    @staticmethod
    def get_homeworks_id(db: Session, school_id: int | None = None, teacher_id: int | None =  None, group_id: int | None = None):
        try:
            query = db.query(Homework)
            if school_id != None:
                query = query.filter(Homework.school_id==school_id)
            if teacher_id != None: 
                query = query.filter(Homework.teacher_id==teacher_id)
            if group_id != None:
                query = query.filter(Homework.group_id == group_id)
            return query.all()
        except SQLAlchemyError as e:
            logger.error(f'Error in db: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

    @staticmethod
    def get_homework_id(db: Session, homework_id: int):
        try:
            return db.query(Homework).get(homework_id)
        except SQLAlchemyError as e:
            logger.error(f'Error in db: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise
