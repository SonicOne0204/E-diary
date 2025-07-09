from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.services.teacher_service import TeacherService
from app.db.core import get_db
from app.exceptions.teachers import TeacherAlreadyAssigned, TeacherNotFound
from app.exceptions.students import StudentAlreadyAssigned, StudentNotFound
from app.exceptions.schedules import ScheduleNotFound
from app.schemas.teachers import MarkPresenceData
from app.schemas.attendance import AttendanceOut

import logging
logger = logging.getLogger(__name__)

teacher_router = APIRouter(
    prefix='/teacher',
    tags=['teacher']
    )

@teacher_router.post(path='/mark-attendance', response_model=AttendanceOut)
def mark_attendance_id(db: Annotated[Session, Depends(get_db)], data: MarkPresenceData):
    try:
        attendance = TeacherService.mark_presence(db=db, student_id=data.student_id, lesson_id=data.lesson_id, teacher_id=data.teacher_id, status=data.status)
        return attendance
    except TeacherNotFound:
        logger.info(f'Teacher with id {data.teacher_id} is not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such teacher')
    except StudentNotFound:
        logger.info(f'Student with id {data.student_id} is not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such Student')
    except ScheduleNotFound:
        logger.info(f'Schedule with id {data.schedule_id} is not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such lesson')
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)