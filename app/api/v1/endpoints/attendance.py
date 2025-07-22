from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from app.crud.attendance import AttendanceCRUD
from app.db.core import get_db
from app.schemas.attendance import StatusOptions
from app.schemas.users import UserTypes
from app.db.models.attendance import Attendance
from app.db.models.users import User 
from app.services.auth import get_current_user
from app.exceptions.basic import NotFound, NotAllowed
from app.dependecies.auth import check_role

import logging
logger = logging.getLogger(__name__)

attendances_router = APIRouter(
    prefix='/attendances',
    tags=['attendances']
)

    
@attendances_router.get('/', dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal, UserTypes.student, UserTypes.teacher]))])
def get_attendances(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)] ,school_id: int , group_id: int | None = None, teacher_id: int | None = None, status_option: StatusOptions | None = None):
    try:
        attendances: list[Attendance] = AttendanceCRUD.get_attendances_id(db=db, user=user ,school_id=school_id, group_id=group_id, teacher_id=teacher_id, status=status_option)
        return attendances
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='attendances not found')
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@attendances_router.get('/{attendance_id}', dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal, UserTypes.student, UserTypes.teacher]))])
def get_attendance(db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)], attendance_id: int):
    try:
        attendance = AttendanceCRUD.get_attendance_id(db=db, user=user ,attendance_id=attendance_id)
        return attendance
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Attendance not found')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@attendances_router.delete('/{attendance_id}', dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal, UserTypes.teacher]))])
def delete_attendance(db: Annotated[Session,Depends(get_db)], user: Annotated[User, Depends(get_current_user)] ,attendance_id: int):
    try:
        AttendanceCRUD.delete_attendance(db=db, user=user ,attendance_id=attendance_id)
        return {"detail": f"attendance with id {attendance_id} was deleted"}
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='attendance not found')
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Cannot delete: related records exist")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)