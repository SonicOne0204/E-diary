from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from app.crud.homeworks import HomeworkCRUD
from app.db.core import get_db
from app.schemas.homeworks import HomeworkData, HomeworkDataUpdate
from app.db.models.homeworks import Homework
from app.db.models.users import User
from app.exceptions.basic import NotFound, NotAllowed
from app.dependecies.auth import check_role, get_current_user
from app.schemas.auth import UserTypes

import logging
logger = logging.getLogger(__name__)

homeworks_router = APIRouter(
    prefix='/homeworks',
    tags=['homeworks']
)

@homeworks_router.post('/', status_code=status.HTTP_201_CREATED ,response_model=HomeworkData, dependencies=[Depends(check_role([UserTypes.admin , UserTypes.teacher]))])
def add_homework(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)] , data: HomeworkData) -> Homework:
    try:
        homework: Homework = HomeworkCRUD.add_homework(db=db, user=user ,data=data)
        return homework
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'No such school with id {homework.school_id}')
    except NotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to give homework')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@homeworks_router.get('/', dependencies=[Depends(check_role([UserTypes.admin, UserTypes.teacher, UserTypes.principal, UserTypes.student]))])
def get_homeworks(
    db: Annotated[Session, Depends(get_db)], 
    user: Annotated[User, Depends(get_current_user)] ,
    school_id: int, group_id: int | None = None, 
    teacher_id: int | None = None) -> list[Homework]:
    try:
        homeworks: list[Homework] = HomeworkCRUD.get_homeworks_id(db=db, user=user ,school_id=school_id, group_id=group_id, teacher_id=teacher_id)
        return homeworks
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='homeworks not found')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@homeworks_router.get('/{homework_id}')
def get_homework(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], homework_id: int) -> Homework:
    try:
        homework = HomeworkCRUD.get_homework_id(db=db,user=user ,homework_id=homework_id)
        return homework
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@homeworks_router.delete('/{homework_id}')
def delete_homework(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], homework_id: int) -> None:
    try:
        HomeworkCRUD.delete_homework(db=db,user=user ,homework_id=homework_id)
        logger.debug(f"Homework with id {homework_id} was deleted")
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='homework not found')
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Cannot delete: related records exist")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@homeworks_router.patch('/{homework_id}')
def update_homework(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], homework_id: int, data: HomeworkDataUpdate) -> Homework:
    try:
        updated_homework = HomeworkCRUD.update_homework(db=db, user=user ,homework_id=homework_id, data=data)
        return updated_homework
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't update data. Please check data validity")
    except NotAllowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not allowed to give homework')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)