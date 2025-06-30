from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.services.principal_service import PrincipalService
from app.db.core import get_db
from app.schemas.principals import AssignStudentByIdSchoolModel, AssignTeacherByIdSchoolModel, AssingStudentByIdGroupModel, AssingTeacherByIdSubjectModel
from app.exceptions.teachers import TeacherAlreadyAssigned, TeacherNotFound
from app.exceptions.students import StudentAlreadyAssigned, StudentNotFound

import logging
logger = logging.getLogger(__name__)

principal_router = APIRouter(
    prefix='/principal',
    tags=['principal']
    )

@principal_router.post(path='/assign-teacher')
def assign_teacher_to_school_id(db: Annotated[Session, Depends(get_db)], data: AssignTeacherByIdSchoolModel):
    try:
        PrincipalService.link_teacher_to_school_id(db=db, school_id= data.school_id, teacher_id=data.teacher_id)
        return {
            f'Teacher with id {data.teacher_id}': f'Assigned to school id = {data.school_id}'
        }
    except TeacherNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such teacher username')
    except TeacherAlreadyAssigned:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Teacher already assigned to other school')
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='No such school id. Cannot assign teacher')
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@principal_router.post(path='/assign-student/school')
def assign_student_to_school_by_id(db: Annotated[Session, Depends(get_db)], data: AssignStudentByIdSchoolModel):
    try:
        PrincipalService.link_student_to_school_id(db=db, school_id= data.school_id, student_id=data.student_id)
        return {
            f'Student with id {data.student_id}': f'Assigned to school id = {data.school_id}'
        }
    except StudentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such student username')
    except StudentAlreadyAssigned:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='student already assigned to other school')
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='No such school id. Cannot assign student')
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@principal_router.post(path='/assign-student/group')
def assign_student_to_group_by_id(db: Annotated[Session, Depends(get_db)], data: AssingStudentByIdGroupModel):
    try:
        PrincipalService.link_student_to_group_id(db=db, group_id=data.group_id, student_id=data.student_id)
        return {
            f'Student with id {data.student_id}': f'Assigned to group id = {data.group_id}'
        }
    except StudentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such student username')
    except StudentAlreadyAssigned:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='student already assigned to other group')
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='No such group id. Cannot assign student')
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@principal_router.post(path='/assign-teacher/subject')
def assign_student_to_subject_by_id(db: Annotated[Session, Depends(get_db)], data: AssingTeacherByIdSubjectModel):
    try:
        PrincipalService.link_teacher_to_subject_id(db=db, teacher_id=data.teacher_id, subject_id=data.subject_id)
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)