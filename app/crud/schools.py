from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.models.schools import School
from app.schemas.schools import SchoolData, SchoolUpdate
from app.exceptions.basic import NotFound, NotAllowed

import logging

logger = logging.getLogger(__name__)

class SchoolCRUD():
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
        except Exception as e:
            logger.exception(f'Unexcpeted error occured: {e}')
            raise
    @staticmethod
    def delete_school(db: Session, school_id: int) -> dict:
        school: School = db.query(School).get(school_id)
        if school == None:
            raise NotFound('No such school')
        db.delete(school)
        try:
            db.commit()
            logger.info(f'School with name {school.name} is deleted')
            return {f'School id {school_id}': 'Deleted succesfully'}
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'DB error occured: {e}')
            raise RuntimeError('Error in DB occured')
        except Exception as e:
            logger.exception(f'Unexcpeted error occured: {e}')
            raise
    

    @staticmethod
    def update_school_data(db: Session, school_id: int , data: SchoolUpdate) -> School:
        school: School = db.query(School).get(school_id)
        if school == None:
            raise NotFound('No such school')
        try:
            for key, value in data.model_dump(exclude_unset=True).items():
                setattr(school, key, value)
            db.commit()
            db.refresh(school)
            return school
        except IntegrityError as e:
            db.rollback()
            logger.error(f'Integrity error occured: {e}')
            raise ValueError(f'School name "{school.name}" is already taken')
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Unexpected error in DB occured: {e}')
            raise RuntimeError('Unexcpeted error in DB')
        except Exception as e:
            logger.exception(f'Unexcpeted error occured: {e}')
            raise

        
    @staticmethod
    def get_school(db: Session, name: str | None = None, school_id: int | None = None) -> School:
        try:
            if name and school_id:
                raise NotAllowed('Can\'t use both query parameters')
            if name != None:
                school = db.query(School).filter(School.name == name).one_or_none()
            if school_id != None:
                school = db.query(School).filter(School.id == school_id).one_or_none()
            if school == None:
                logger.info(f'School with id {school_id} or name \'{name}\' is not found')
                raise NotFound('No such school')
            return school
        except Exception as e:
            logger.exception(f'Unexcpeted error occured: {e}')
            raise

    @staticmethod
    def get_schools(db: Session, country: str | None = None, is_active: bool | None = None) -> list['School']:
        try:
            query = db.query(School)
            if country is not None:
                query = query.filter(School.country == country)
            if is_active is not None:
                query = query.filter(School.is_active == is_active)
            return query.all()
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise


    

    