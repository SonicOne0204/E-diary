from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.schemas.groups import GroupData
from app.db.models.groups import Group
from app.exceptions.basic import NotFound

import logging
logger = logging.getLogger(__name__)

class GroupCRUD():
    @staticmethod
    def add_group(db: Session, data: GroupData):
        try:
            group = Group()
            for key, value in data.model_dump().items():
                setattr(group, key, value)
            db.add(group)
            db.commit()
            db.refresh(group)
            return group
        except IntegrityError:
            db.rollback()
            raise 
        except SQLAlchemyError:
            db.rollback()
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise
    
    @staticmethod
    def delete_group(db: Session, group_id: int):
        try:
            group = db.query(Group).get(group_id)
            if not group:
                logger.info(f'Group with id {group_id} not found')
                raise NotFound('Group not found')    
            db.delete(group)
            db.commit()
        except IntegrityError as e:
            logger.error(f'Integrity error: {e}')
            db.rollback()
            raise 
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise
    
    @staticmethod     
    def update_group(db: Session, group_id: int , data: GroupData):
        try:
            group = db.query(Group).get(group_id)
            for key, value in data.model_dump().items():
                setattr(group, key, value)
            db.commit()
            db.refresh(group)
            return group
        except IntegrityError:
            logger.error
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise
    
    @staticmethod
    def get_groups(db: Session, school_id: int):
        try:
            groups = db.query(Group).filter(Group.school_id == school_id).all()
            if not groups:
                logger.info(f'Groups with school id {school_id} not found')
                return NotFound('Group not found')
            return groups
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise
    @staticmethod 
    def get_group(db: Session, group_id: int):
        try:
            group = db.query(Group).get(group_id)
            if not group:
                logger.info(f'Groups with id {group_id} not found')
                raise NotFound
            return group
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise