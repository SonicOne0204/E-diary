from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.core import get_db
from app.db.models.users import User
from app.dependecies.auth import get_current_user
from app.services.grades_service import GradeService

import logging

logger = logging.getLogger(__name__)

grades_router = APIRouter(prefix="/grades", tags=["grades"])


@grades_router.post("/average")
def average_grades_student(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict:
    try:
        return GradeService(db=db, student=user)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
