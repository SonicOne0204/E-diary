from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.db.models.schools import School
from app.schemas.schools import SchoolData, SchoolUpdate
from app.schemas.users import UserTypes
from app.exceptions.basic import NotFound, NotAllowed
from app.db.models.users import User
from app.db.models.types import Teacher, Student, Principal

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
            logger.error(f'Integrity error occurred: {e}')
            raise ValueError(f'This schoolname already exists: {school.name}')
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'DB error: {e}')
            raise RuntimeError('Database error')
        except Exception as e:
            db.rollback()
            logger.exception(f'Unexpected error: {e}')
            raise

    @staticmethod
    def delete_school(db: Session, user: User, school_id: int) -> dict:
        school: School = db.query(School).get(school_id)
        if school is None:
            logger.warning(f"User {user.id} ({user.type}) tried to delete non-existent school ID {school_id}")
            raise NotFound("No such school")

        if user.type == UserTypes.principal:
            principal: Principal = db.query(Principal).get(user.id)
            if principal.school_id != school_id:
                logger.warning(f"Principal {user.id} tried to delete school {school_id} not assigned to them")
                raise NotAllowed("Not allowed to delete this school")
        elif user.type != UserTypes.admin:
            logger.warning(f"User {user.id} ({user.type}) tried to delete school {school_id} without permission")
            raise NotAllowed("Only admins or assigned principals can delete schools")

        try:
            db.delete(school)
            db.commit()
            logger.info(f"School ID {school_id} deleted by user {user.id} ({user.type})")
            return {f"School ID {school_id}": "Deleted successfully"}
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"DB error while deleting school {school_id}: {e}")
            raise
        except Exception as e:
            db.rollback()
            logger.exception(f"Unexpected error while deleting school {school_id}: {e}")
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
    def get_school(db: Session, user: User, name: str | None = None, school_id: int | None = None) -> School:
        try:
            if name and school_id:
                logger.warning(f"User {user.id} sent conflicting params: name='{name}' and id={school_id}")
                raise NotAllowed("Can't use both query parameters")

            school = None
            if name is not None:
                school = db.query(School).filter(School.name == name).one_or_none()
            elif school_id is not None:
                school = db.query(School).filter(School.id == school_id).one_or_none()
            else:
                logger.warning(f"User {user.id} requested school without providing name or ID")
                raise ValueError("Must provide either school name or ID")

            if school is None:
                logger.info(f"School not found (name='{name}', id={school_id}) by user {user.id}")
                raise NotFound("No such school")
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if principal.school_id != school.id:
                    logger.warning(f"Principal {user.id} tried to access school {school.id}")
                    raise NotAllowed("Cannot access this school")
            elif user.type == UserTypes.teacher:
                teacher: Teacher = db.query(Teacher).get(user.id)
                if teacher.school_id != school.id:
                    logger.warning(f"Teacher {user.id} tried to access school {school.id}")
                    raise NotAllowed("Cannot access this school")
            elif user.type == UserTypes.student:
                student: Student = db.query(Student).get(user.id)
                if student.school_id != school.id:
                    logger.warning(f"Student {user.id} tried to access school {school.id}")
                    raise NotAllowed("Cannot access this school")
            return school
        except Exception as e:
            logger.exception(f"Unexpected error in get_school by user {user.id}: {e}")
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


    

    