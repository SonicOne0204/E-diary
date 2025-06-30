from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.models.schools import School
from app.schemas.schools import SchoolData, SchoolUpdate
from app.exceptions.school import SchoolNotFound

import logging

logger = logging.getLogger(__name__)

class SchoolCRUD():
    '''
    Do not forget to add access restriction depending on user type     
    '''
    @staticmethod
    def create_school(db: Session, data: SchoolData) -> School:
        school = School()
        try:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(school, key, value)
            db.add(school)
            db.commit()
            db.refresh(school)
            return school
        except IntegrityError as e:
            db.rollback()
            logger.error(f'Integrity error occured: {e}')
            raise ValueError(f'This schoolname already exists: {school.name}')
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error getting db: {e}')
            raise RuntimeError('Error in DB')
    
    @staticmethod
    def delete_school(db: Session, school_id: int):
        school: School = db.query(School).get(school_id)
        if school == None:
            raise SchoolNotFound('No such school')
        db.delete(school)
        try:
            db.commit()
            logger.info(f'School with name {school.name} is deleted')
            return {f'School id {school_id}': 'Deleted succesfully'}
        except SQLAlchemyError as e:
            logger.error(f'DB error occured: {e}')
            raise RuntimeError('Error in DB occured')
    

    @staticmethod
    def update_school_data(db: Session, school_id: int , data: SchoolUpdate):
        school: School = db.query(School).get(school_id)
        if school == None:
            raise SchoolNotFound('No such school')
        try:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(school, key, value)
            db.commit()
            db.refresh(school)
            return school
        except IntegrityError as e:
            logger.error(f'Integrity error occured: {e}')
            raise ValueError(f'School name "{school.name}" is already taken')
        except SQLAlchemyError as e:
            logger.error(f'Unexpected error in DB occured: {e}')
            raise RuntimeError('Unexcpeted error in DB')

        
    @staticmethod
    def get_school(db: Session, name: str):
        school = db.query(School).filter(School.name == name).one_or_none()
        if school == None:
            raise SchoolNotFound('No such school')
        return school
    

    