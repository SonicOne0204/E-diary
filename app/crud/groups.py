from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.schemas.groups import GroupData
from app.db.models.groups import Group
from app.exceptions.basic import NotFound, NotAllowed
from app.db.models.users import User
from app.db.models.types import Principal
from app.schemas.users import UserTypes

import logging
logger = logging.getLogger(__name__)

class GroupCRUD():
    @staticmethod
    def add_group(db: Session, user: User ,data: GroupData):
        try:
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if principal.school_id != data.school_id:
                    logger.warning(f'User with id {user.id} tried to create group in school with id {data.school_id}. Not allowed')
                    raise NotAllowed('Cannot access other schools')
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
    def delete_group(db: Session, user: User ,group_id: int):
        try:
            group: Group = db.query(Group).get(group_id)
            if not group:
                logger.info(f'Group with id {group_id} not found')
                raise NotFound('Group not found')
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if principal.school_id != group.school_id:
                    logger.warning(f'User with id {user.id} tried to create group in school with id {group.school_id}. Not allowed')
                    raise NotAllowed('Cannot access other schools')    
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
    def update_group(db: Session, user: User, group_id: int , data: GroupData):
        try:
            group: Group = db.query(Group).get(group_id)
            if not group:
                logger.info(f'Group with id {group_id} not found')
                raise NotFound('Group not found')
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if principal.school_id != group.school_id:
                    logger.warning(f'User with id {user.id} tried to create group in school with id {group.school_id}. Not allowed')
                    raise NotAllowed('Cannot access other schools') 
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
    def get_groups(db: Session, user: User, school_id: int):
        try:
            groups = db.query(Group).filter(Group.school_id == school_id).all()
            if not groups:
                logger.info(f'Groups with school id {school_id} not found')
                return NotFound('Group not found')
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if principal.school_id != school_id:
                    logger.warning(f'User with id {user.id} tried to create group in school with id {school_id}. Not allowed')
                    raise NotAllowed('Cannot access other schools') 
            return groups
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise
    @staticmethod 
    def get_group(db: Session, user: User ,group_id: int):
        try:
            group: Group = db.query(Group).get(group_id)
            if not group:
                logger.info(f'Groups with id {group_id} not found')
                raise NotFound
            if user.type == UserTypes.principal:
                principal: Principal = db.query(Principal).get(user.id)
                if principal.school_id != group.school_id:
                    logger.warning(f'User with id {user.id} tried to create group in school with id {group.school_id}. Not allowed')
                    raise NotAllowed('Cannot access other schools') 
            return group
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise