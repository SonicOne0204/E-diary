from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.services.teacher_service import TeacherService
from app.db.core import get_db
from app.exceptions.teachers import TeacherAlreadyAssigned, TeacherNotFound
from app.exceptions.students import StudentAlreadyAssigned, StudentNotFound
from app.exceptions.schedules import ScheduleNotFound
from app.exceptions.basic import NoDataError
from app.schemas.teachers import MarkPresenceData
from app.schemas.attendance import AttendanceOut
from app.schemas.grades import AssignGradeData, GradeDataOut

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
    
@teacher_router.post(path='/assign-grade', response_model=GradeDataOut)
def assign_grade(db: Annotated[Session, Depends(get_db)], data: AssignGradeData):
    try:
        attendance = TeacherService.assign_grade(db=db, data=data)
        return attendance
    except NoDataError as e:
        logger.info(f'No full data passed: {e}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Value or grade system is blank')
    except IntegrityError as e:
        if 'unique constraint' in str(e.orig):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This grade is already assigned')
        if '"schedules"' in str(e.orig):
            logger.info(f'Schedule with id {data.schedule_id} is not found')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such lesson/schedule')
        if '"students"' in str(e.orig):
            logger.info(f'Student with id {data.student_id} is not found')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such Student')
        if '"teachers"' in str(e.orig):
            logger.info(f'Teacher with id {data.marked_by} is not found')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such teacher')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)