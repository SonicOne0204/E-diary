from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.services.student_service import StudentService
from app.db.core import get_db
from app.exceptions.students import StudentAlreadyAssigned
from app.exceptions.students import StudentAlreadyAssigned
from app.exceptions.basic import NoDataError, NotAllowed, NotFound
from app.schemas.attendance import AttendanceOut
from app.schemas.grades import AssignGradeData, GradeDataOut
from app.db.models.users import User
from app.services.auth import get_current_user

import logging
logger = logging.getLogger(__name__)

student_router = APIRouter(
    prefix='/student',
    tags=['student']
    )

@student_router.post("/{invitation_id}/accept")
def accept_invitation_endpoint(invitation_id: int,db: Annotated[Session, Depends(get_db)], user: Annotated[User, Depends(get_current_user)]) -> dict:
    try:
        return StudentService.accept_invitation(db=db, user=user, invitation_id=invitation_id)
    except NotFound as e:
        if 'invitation' in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
        if 'student' in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")