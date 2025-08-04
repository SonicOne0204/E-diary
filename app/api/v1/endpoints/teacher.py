from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.teacher_service import TeacherService
from app.db.core import get_db
from app.exceptions.basic import NoDataError, NotAllowed, NotFound
from app.schemas.teachers import MarkPresenceData
from app.schemas.attendance import AttendanceOut
from app.schemas.grades import AssignGradeData, GradeDataOut
from app.schemas.users import UserTypes
from app.db.models.users import User
from app.db.models.grades import Grade
from app.db.models.attendance import Attendance
from app.services.auth import get_current_user
from app.dependecies.auth import check_role

import logging
logger = logging.getLogger(__name__)

teacher_router = APIRouter(
    prefix='/teacher',
    tags=['teacher'],
    dependencies=[Depends(check_role([UserTypes.admin, UserTypes.teacher]))]
    )

@teacher_router.post(path='/mark-attendance', response_model=AttendanceOut)
def mark_attendance_id(db: Annotated[Session, Depends(get_db)], data: MarkPresenceData, user: Annotated[User, Depends(get_current_user)]) -> Attendance:
    try:
        attendance = TeacherService.mark_presence(db=db, user=user ,student_id=data.student_id, lesson_id=data.lesson_id, teacher_id=data.teacher_id, status=data.status)
        return attendance
    except NotFound as e:
        if 'teacher' in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such teacher')
        elif 'student' in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such Student')
        elif 'schedule' in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such lesson')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@teacher_router.post(path='/assign-grade', response_model=GradeDataOut)
def assign_grade(db: Annotated[Session, Depends(get_db)], data: AssignGradeData, user: Annotated[User, Depends(get_current_user)]) -> Grade:
    try:
        grade = TeacherService.assign_grade(db=db, user=user ,data=data)
        return grade
    except NoDataError as e:
        logger.info(f'No full data passed: {e}')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Value or grade system is blank')
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except IntegrityError as e:
        if 'unique constraint' in str(e.orig):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This grade is already assigned')
        elif '"schedules"' in str(e.orig):
            logger.info(f'Schedule with id {data.schedule_id} is not found')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such lesson/schedule')
        elif '"students"' in str(e.orig):
            logger.info(f'Student with id {data.student_id} is not found')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such Student')
        elif '"teachers"' in str(e.orig):
            logger.info(f'Teacher with id {data.marked_by} is not found')
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such teacher')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@teacher_router.post("/{invitation_id}/accept", status_code=200)
def accept_invitation_endpoint(invitation_id: int,db: Annotated[Session, Depends(get_db)],user: Annotated[User, Depends(get_current_user)]) -> dict:
    try:
        return TeacherService.accept_invitation(db=db, user=user, invitation_id=invitation_id)
    except NotFound as e:
        if 'invitation' in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
        if 'teacher' in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
