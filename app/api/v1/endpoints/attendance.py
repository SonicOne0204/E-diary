from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from app.crud.attendance import AttendanceCRUD
from app.db.core import get_db
from app.schemas.attendance import StatusOptions
from app.schemas.users import UserTypes
from app.db.models.attendance import Attendance
from app.db.models.users import User
from app.services.auth import get_current_user
from app.exceptions.basic import NotFound
from app.dependecies.auth import check_role

import logging

logger = logging.getLogger(__name__)

attendances_router = APIRouter(prefix="/attendances", tags=["attendances"])


@attendances_router.get(
    "/",
    dependencies=[
        Depends(
            check_role(
                [
                    UserTypes.admin,
                    UserTypes.principal,
                    UserTypes.student,
                    UserTypes.teacher,
                ]
            )
        )
    ],
)
async def get_attendances(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    school_id: int,
    group_id: int | None = None,
    teacher_id: int | None = None,
    status_option: StatusOptions | None = None,
):
    try:
        attendances: list[Attendance] = await AttendanceCRUD.get_attendances_id(
            db=db,
            user=user,
            school_id=school_id,
            group_id=group_id,
            teacher_id=teacher_id,
            status=status_option,
        )
        return attendances
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="attendances not found"
        )
    except Exception as e:
        logger.exception(f"Error fetching attendances: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@attendances_router.get(
    "/{attendance_id}",
    dependencies=[
        Depends(
            check_role(
                [
                    UserTypes.admin,
                    UserTypes.principal,
                    UserTypes.student,
                    UserTypes.teacher,
                ]
            )
        )
    ],
)
async def get_attendance(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    attendance_id: int,
):
    try:
        attendance = await AttendanceCRUD.get_attendance_id(
            db=db, user=user, attendance_id=attendance_id
        )
        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Attendance not found"
            )
        return attendance
    except Exception as e:
        logger.exception(f"Error fetching attendance {attendance_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@attendances_router.delete(
    "/{attendance_id}",
    dependencies=[
        Depends(check_role([UserTypes.admin, UserTypes.principal, UserTypes.teacher]))
    ],
)
async def delete_attendance(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    attendance_id: int,
):
    try:
        await AttendanceCRUD.delete_attendance(
            db=db, user=user, attendance_id=attendance_id
        )
        return {"detail": f"attendance with id {attendance_id} was deleted"}
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="attendance not found"
        )
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Cannot delete: related records exist"
        )
    except Exception as e:
        logger.exception(f"Error deleting attendance {attendance_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
