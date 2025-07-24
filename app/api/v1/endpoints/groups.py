from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from app.crud.groups import GroupCRUD
from app.db.core import get_db
from app.schemas.groups import GroupData, GroupDataOut
from app.schemas.users import UserTypes
from app.db.models.groups import Group
from app.exceptions.basic import NotFound
from app.db.models.users import User
from app.services.auth import get_current_user
from app.dependecies.auth import check_role

import logging
logger = logging.getLogger(__name__)

groups_router = APIRouter(
    prefix='/groups',
    tags=['groups'],
    dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))]
)

@groups_router.post('/', status_code = status.HTTP_201_CREATED , response_model=GroupDataOut)
def add_group(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)] , data: GroupData) -> Group:
    try:
        group = GroupCRUD.add_group(db=db, user=user ,data=data)
        return group
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'No such school')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@groups_router.get('/schools/{school_id}')
def get_groups(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)] , school_id: int) -> list[Group]:
    try:
        groups: list[Group] = GroupCRUD.get_groups(db=db, user=user ,school_id=school_id)
        return groups
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Groups not found')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@groups_router.get('/{group_id}', response_model=GroupData)
def get_group(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)] , group_id: int) -> Group:
    try:
        group = GroupCRUD.get_group(db=db, user=user ,group_id=group_id)
        return group
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='No such school')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@groups_router.delete('/{group_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_group(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)] , group_id: int) -> None:
    try:
        GroupCRUD.delete_group(db=db, user=user ,group_id=group_id)
        logger.debug(f"Homework with id {group_id} was deleted")
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Group not found')
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Cannot delete: related records exist")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@groups_router.patch('/{group_id}')
def update_group(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)] , group_id: int, data: GroupData) -> Group:
    try:
        updated_group = GroupCRUD.update_group(db=db, user=user ,group_id=group_id, data=data)
        return updated_group
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't update data. Please check data validity")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


