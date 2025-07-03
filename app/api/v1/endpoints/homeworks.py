from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from app.crud.homeworks import HomeworkCRUD
from app.db.core import get_db
from app.schemas.homeworks import HomeworkData, HomeworkDataUpdate
from app.db.models.homeworks import Homework
from app.exceptions.homeworks import HomeworkNotFound

import logging
logger = logging.getLogger(__name__)

homeworks_router = APIRouter(
    prefix='/homeworks',
    tags=['homeworks']
)

@homeworks_router.post('/', response_model=HomeworkData)
def add_homework(db: Annotated[Session, Depends(get_db)], data: HomeworkData):
    try:
        homework = HomeworkCRUD.add_homework(db=db, data=data)
        return homework
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'No such school with id {homework.school_id}')
    except Exception as e:
        logger.exception(f'Unexpected error occured:{e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@homeworks_router.get('/')
def get_homeworks(db: Annotated[Session, Depends(get_db)], school_id: int | None = None, group_id: int | None = None, teacher_id: int | None = None):
    try:
        homeworks: list[Homework] = HomeworkCRUD.get_homeworks_id(db=db, school_id=school_id, group_id=group_id, teacher_id=teacher_id)
        return homeworks
    except HomeworkNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='homeworks not found')
    except Exception as e:
        logger.exception(f'Unexpected error occured:{e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@homeworks_router.get('/{homework_id}')
def get_homework(db: Annotated[Session, Depends(get_db)], homework_id: int):
    try:
        homework = HomeworkCRUD.get_homework_id(db=db, homework_id=homework_id)
        return homework
    except Exception as e:
        logger.exception(f'Unexpected error occured:{e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@homeworks_router.delete('/{homework_id}')
def delete_homework(db: Annotated[Session, Depends(get_db)], homework_id: int):
    try:
        HomeworkCRUD.delete_homework(db=db, homework_id=homework_id)
        return {"detail": f"Homework with id {homework_id} was deleted"}
    except HomeworkNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='homework not found')
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Cannot delete: related records exist")
    except Exception as e:
        logger.exception(f'Unexcpected error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@homeworks_router.patch('/{homework_id}')
def update_homework(db: Annotated[Session, Depends(get_db)], homework_id: int, data: HomeworkDataUpdate):
    try:
        updated_homework = HomeworkCRUD.update_homework(db=db, homework_id=homework_id, data=data)
        return updated_homework
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't update data. Please check data validity")
    except Exception as e:
        logger.exception(f'Unexcpected error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)