from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.db.core import get_async_db
from app.db.models.users import User
from app.dependecies.auth import get_current_user
from app.services.grades_service import GradeService
from app.exceptions.basic import NotAllowed, NotFound, NoDataError

import logging

logger = logging.getLogger(__name__)

grades_router = APIRouter(prefix="/grades", tags=["grades"])


@grades_router.get("/students/{student_id}/average/")
async def average_grades_student(
    db: Annotated[Session, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    student_id: int,
) -> dict:
    try:
        return await GradeService(db=db, user=user, student_id=student_id).average()
    except NotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except NoDataError:
        return {"message": "Student doesn't have grades yet"}
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
