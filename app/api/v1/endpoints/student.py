from fastapi import APIRouter, Depends, Path, HTTPException, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.student_service import StudentService
from app.db.core import get_async_db
from app.exceptions.basic import NotAllowed, NotFound
from app.db.models.users import User
from app.services.auth import get_current_user

import logging

logger = logging.getLogger(__name__)

student_router = APIRouter(prefix="/students", tags=["students"])


@student_router.post("/invitations/{invitation_id}/")
async def accept_invitation_endpoint(
    invitation_id: Annotated[int, Path()],
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    try:
        return await StudentService.accept_invitation(
            db=db, user=user, invitation_id=invitation_id
        )
    except NotFound as e:
        msg = str(e).lower()
        if "invitation" in msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found"
            )
        if "student" in msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
