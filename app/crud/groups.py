from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.schemas.groups import GroupData
from app.db.models.groups import Group
from app.exceptions.groups import GroupNotFound

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
    
    @staticmethod
    def delete_group(db: Session, group_id: int):
        try:
            group = db.query(Group).get(group_id)
            if not group:
                raise GroupNotFound()    
            db.delete(group)
            db.commit()
        except IntegrityError as e:
            logger.error(f'Integrity error: {e}')
            db.rollback()
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
            raise
    
    @staticmethod
    def get_groups(db: Session, school_id: int):
        groups = db.query(Group).filter(Group.school_id == school_id).all()
        if not groups:
            return GroupNotFound()
        return groups
    
    @staticmethod 
    def get_group(db: Session, group_id: int):
        group = db.query(Group).get(group_id)
        if group:
            return group
        raise GroupNotFound
