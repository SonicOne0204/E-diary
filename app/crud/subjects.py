from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.models import Subject
from app.schemas.subjects import SubjectData, SubjectUpdate
from app.exceptions.subject import SubjectNotFound

import logging

logger = logging.getLogger(__name__)

class SubjectCRUD():
    @staticmethod
    def create_subject(db: Session, data: SubjectData) -> Subject:
        subject = Subject()
        try:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(subject, key, value)
            db.add(subject)
            db.commit()
            db.refresh(subject)
            return subject
        except IntegrityError as e:
            db.rollback()
            logger.error(f'Integrity error occured: {e}')
            raise ValueError(f'This subject name already exists: {subject.name}')
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error getting db: {e}')
            raise RuntimeError('Error in DB')
        
    @staticmethod
    def delete_subject(db: Session, subject_id: int):
        subject: Subject = db.query(subject).get(subject_id)
        if subject == None:
            raise SubjectNotFound()
        db.delete(subject)
        try:
            db.commit()
            logger.info(f'subject with name {subject.name} is deleted')
            return {f'subject id {subject_id}': 'Deleted succesfully'}
        except SQLAlchemyError as e:
            logger.error(f'DB error occured: {e}')
            raise RuntimeError('Error in DB occured')
        
    @staticmethod
    def update_subject_data(db: Session, subject_id: int , data: SubjectUpdate):
        subject: Subject = db.query(Subject).get(subject_id)
        if subject == None:
            raise subjectNotFound('No such subject')
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
    def get_subject(db: Session, name: str):
        subject = db.query(Subject).filter(Subject.name == name).one_or_none()
        if subject == None:
            raise SubjectNotFound()
        return subject