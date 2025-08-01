from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.services.principal_service import PrincipalService
from app.db.core import get_db
from app.db.models.users import User
from app.db.models.invitations import Invitation
from app.schemas.principals import InviteStudentByIdSchoolModel, InviteTeacherByIdSchoolModel, AssingStudentByIdGroupModel, AssingTeacherByIdSubjectModel
from app.exceptions.teachers import TeacherAlreadyAssigned
from app.exceptions.students import StudentAlreadyAssigned
from app.exceptions.basic import NotFound
from app.schemas.users import UserTypes
from app.schemas.invitations import InvitationOut
from app.dependecies.auth import check_role, get_current_user


import logging
logger = logging.getLogger(__name__)

principal_router = APIRouter(
    prefix='/principal',
    tags=['principal'],
    dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))]
    )

@principal_router.post(path='/assign-teacher', response_model=InvitationOut)
def invite_teacher_to_school_id(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)] ,data: InviteTeacherByIdSchoolModel) -> Invitation:
    try:
        invitation = PrincipalService.invite_teacher_to_school_id(db=db, school_id=data.school_id, user=user ,teacher_id=data.teacher_id)
        return invitation
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such teacher')
    except TeacherAlreadyAssigned:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Teacher already assigned to other school')
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='No such school id. Cannot assign teacher')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@principal_router.post(path='/assign-student/school', response_model=InvitationOut)
def invite_student_to_school_by_id(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)] ,data: InviteStudentByIdSchoolModel) -> Invitation:
    try:
        invitation = PrincipalService.invite_student_to_school_id(db=db, user=user ,school_id= data.school_id, student_id=data.student_id)
        return invitation
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such student')
    except StudentAlreadyAssigned:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='student already assigned to other school')
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='No such school id. Cannot assign student')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@principal_router.post(path='/assign-student/group')
def assign_student_to_group_by_id(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], data: AssingStudentByIdGroupModel) -> dict:
    try:
        PrincipalService.link_student_to_group_id(db=db, user=user ,group_id=data.group_id, student_id=data.student_id)
        return {
            "detail": f"Student {data.student_id} assigned to group {data.group_id}"
        }
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such student')
    except StudentAlreadyAssigned:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='student already assigned to other group')
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='No such group id. Cannot assign student')
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@principal_router.post(path='/assign-teacher/subject')
def assign_student_to_subject_by_id(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], data: AssingTeacherByIdSubjectModel) -> dict:
    try:
        PrincipalService.link_teacher_to_subject_id(db=db, user=user ,teacher_id=data.teacher_id, subject_id=data.subject_id)
        return {
            "detail": f"Teacher {data.teacher_id} assigned to subject {data.subject_id}"
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)