from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.models.subjects import Subject
from app.db.models.users import User
from app.db.models.types import Teacher, Student, Principal
from app.schemas.subjects import SubjectData, SubjectUpdate
from app.exceptions.basic import NotFound, NotAllowed
from app.schemas.auth import UserTypes

import logging

logger = logging.getLogger(__name__)

class SubjectCRUD():
    @staticmethod
    def create_subject(db: Session, data: SubjectData) -> Subject:
        try:
            subject = Subject()
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(subject, key, value)
            db.add(subject)
            db.commit()
            db.refresh(subject)
            return subject
        except IntegrityError as e:
            db.rollback()
            logger.error(f'Integrity error occured: {e}')
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error getting db: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise
        
    @staticmethod
    def delete_subject(db: Session, user: User ,subject_id: int):
        try:
            subject: Subject = db.query(Subject).get(subject_id)
            if not subject:
                logger.info(f'subject with id {subject_id} is not found')
                raise NotFound(f'subject with id {subject_id} not found')
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if principal.school_id != subject.school_id:
                    logger.warning(f'User with id {user.id} tried to delete subject with id {subject_id}, but from another school')
                    raise NotAllowed('Cannot delete from other schools')
            db.delete(subject)
            db.commit()
            logger.info(f'subject with id {subject_id} was deleted')
            return True
        except SQLAlchemyError as e:
            logger.error(f'Error in db: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise
        
    @staticmethod
    def update_subject_data(db: Session, subject_id: int , data: SubjectUpdate):
        subject: Subject = db.query(Subject).get(subject_id)
        if subject == None:
            logger.info(f'Subject with id {subject_id} not found')
            raise NotFound('No such subject')
        try:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(subject, key, value)
            db.commit()
            db.refresh(subject)
            return subject
        except IntegrityError as e:
            logger.error(f'Integrity error occured: {e}')
            raise ValueError(f'subject name "{subject.name}" is already taken')
        except SQLAlchemyError as e:
            logger.error(f'Unexpected error in DB occured: {e}')
            raise RuntimeError('Unexcpeted error in DB')
        
        
    @staticmethod
    def get_subject_id(db: Session, user: User ,subject_id: int):
        try:
            subject: Subject = db.query(Subject).get(subject_id)
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if principal.school_id != subject.school_id:
                    logger.warning('User with id {user.id} tried to access subject with id {subject_id}. Not allowed to access other schools')
                    raise NotAllowed('Cannot access other schools')
            elif user.type == UserTypes.teacher:
                teacher: Teacher = db.query(Teacher).get(user.id)
                if subject.school_id != teacher.id:
                    logger.warning('User with id {user.id} tried to access subject with id {subject_id}. Not allowed to access other schools')
                    raise NotAllowed('Cannot access subject from other teachers or schools')              
            elif user.type == UserTypes.student:
                student: Student = db.query(Student).get(user.id)
                if subject.school_id!= student.school_id:
                    logger.warning('User with id {user.id} tried to access subject with id {subject_id}. Not allowed to access other schools')
                    raise NotAllowed('Cannot access subject from other schools')
            return subject
        except IntegrityError:
            logger.info(f'Attednace not found with if {subject_id}')
            raise
        except SQLAlchemyError as e:
            logger.error(f'Error in db: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

    @staticmethod
    def get_subjects(db: Session, user: User, school_id: int , name: str | None = None):
        try:
            if user.type == UserTypes.teacher:
                teacher: Teacher = db.query(Teacher).get(user.id)
                if teacher.school_id != school_id:
                    logger.warning(f'User with id {user.id} tried to access subjects from school with id {school_id}. Cannot get from other schools')
                    raise NotAllowed('Cannot get subject from other school')
            elif user.type == UserTypes.student:
                student: Student = db.query(Student).get(user.id)
                if student.school_id != school_id:
                    logger.warning(f'User with id {user.id} tried to access subjects from school with id {school_id}. Cannot get from other schools')
                    raise NotAllowed('Cannot get subject from other school')
            elif user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if principal.school_id != school_id:
                    logger.warning(f'User with id {user.id} tried to access subjects from school with id {school_id}. Cannot get from other schools')
                    raise NotAllowed('Cannot get subject from other school')
            query = db.query(Subject)
            query = query.filter(Subject.school_id == school_id)
            if name:
                query = query.filter(Subject.name == name)
            return query.all()
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

            