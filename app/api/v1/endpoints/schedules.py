from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from app.crud.schedules import ScheduleCRUD
from app.db.core import get_db
from app.schemas.schedules import ScheduleData, ScheduleUpdateData
from app.db.models.schedules import Schedule
from app.exceptions.schedules import ScheduleNotFound
from app.dependecies.auth import check_role

import logging
logger = logging.getLogger(__name__)

schedules_router = APIRouter(
    prefix='/schedules',
    tags=['schedules']
)

@schedules_router.post('/', dependencies=[Depends(check_role('principal'))])
def add_schedule(db: Annotated[Session, Depends(get_db)], data: ScheduleData):
    try:
        schedule = ScheduleCRUD.create_schedule(db=db, data=data)
        return schedule
    except ScheduleNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@schedules_router.get('/')
def get_schedules_today(db: Annotated[Session, Depends(get_db)], school_id: int | None = None, group_id: int | None = None, teacher_id: int | None = None):
    try:
        schedules = ScheduleCRUD.get_schedule_today(db=db, school_id=school_id, group_id=group_id, teacher_id=teacher_id)
        return schedules
    except ScheduleNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='schedules not found')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@schedules_router.get('/{schedule_id}')
def get_schedule(db: Annotated[Session, Depends(get_db)], schedule_id: int):
    try:
        schedule = ScheduleCRUD.get_schedule_id(db=db, schedule_id=schedule_id)
        return schedule
    except ScheduleNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='schedules not found')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@schedules_router.delete('/{schedule_id}')
def delete_schedule(db: Annotated[Session, Depends(get_db)], schedule_id: int):
    try:
        ScheduleCRUD.delete_schedule(db=db, schedule_id=schedule_id)
        return {"detail": f"schedule with id {schedule_id} was deleted"}
    except ScheduleNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='schedule not found')
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Cannot delete: related records exist")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@schedules_router.patch('/{schedule_id}')
def update_schedule(db: Annotated[Session, Depends(get_db)], schedule_id: int, data: ScheduleUpdateData):
    try:
        updated_schedule = ScheduleCRUD.update_schedule(db=db, schedule_id=schedule_id, data=data)
        return updated_schedule
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't update data. Please check data validity")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)