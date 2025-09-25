from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.services.principal_service import PrincipalService
from app.db.core import get_async_db
from app.db.models.users import User
from app.db.models.invitations import Invitation
from app.exceptions.teachers import TeacherAlreadyAssigned
from app.exceptions.students import StudentAlreadyAssigned
from app.exceptions.basic import NotFound
from app.schemas.users import UserTypes
from app.schemas.invitations import InvitationOut
from app.dependecies.auth import check_role, get_current_user

import logging

logger = logging.getLogger(__name__)

principal_router = APIRouter(
    prefix="/principals",
    tags=["principals"],
    dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))],
)


@principal_router.post(
    path="/schools/{school_id}/teachers/{teacher_id}/", response_model=InvitationOut
)
async def invite_teacher_to_school_id(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    school_id: int,
    teacher_id: int,
) -> Invitation:
    try:
        invitation = await PrincipalService.invite_teacher_to_school_id(
            db=db, school_id=school_id, user=user, teacher_id=teacher_id
        )
        return invitation
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such teacher"
        )
    except TeacherAlreadyAssigned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Teacher already assigned to other school",
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No such school id. Cannot assign teacher",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@principal_router.post(
    path="/schools/{school_id}/students/{student_id}/", response_model=InvitationOut
)
async def invite_student_to_school_by_id(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    school_id: int,
    student_id: int,
) -> Invitation:
    try:
        invitation = await PrincipalService.invite_student_to_school_id(
            db=db, user=user, school_id=school_id, student_id=student_id
        )
        return invitation
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such student"
        )
    except StudentAlreadyAssigned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student already assigned to other school",
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No such school id. Cannot assign student",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@principal_router.post(path="/groups/{group_id}/students/{student_id}/")
async def assign_student_to_group_by_id(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    group_id: int,
    student_id: int,
) -> dict:
    try:
        await PrincipalService.link_student_to_group_id(
            db=db, user=user, group_id=group_id, student_id=student_id
        )
        return {"detail": "Student assigned to group"}
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such student"
        )
    except StudentAlreadyAssigned:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student already assigned to other group",
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No such group id. Cannot assign student",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@principal_router.post(path="/subjects/{subject_id}/teachers/{teacher_id}/")
async def assign_teacher_to_subject_by_id(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    subject_id: int,
    teacher_id: int,
) -> dict:
    try:
        await PrincipalService.link_teacher_to_subject_id(
            db=db, user=user, teacher_id=teacher_id, subject_id=subject_id
        )
        return {"detail": "Teacher assigned to subject"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
