from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from app.crud.schedules import ScheduleCRUD
from app.db.core import get_db
from app.schemas.schedules import ScheduleData, ScheduleUpdateData, ScheduleDataOut
from app.db.models.schedules import Schedule
from app.db.models.users import User
from app.exceptions.basic import NotAllowed, NotFound
from app.dependecies.auth import check_role
from app.services.auth import get_current_user
from app.schemas.users import UserTypes

import logging

logger = logging.getLogger(__name__)

schedules_router = APIRouter(prefix="/schedules", tags=["schedules"])


@schedules_router.post(
    "/",
    response_model=ScheduleDataOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))],
)
def add_schedule(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    data: ScheduleData,
) -> Schedule:
    try:
        schedule = ScheduleCRUD.create_schedule(db=db, user=user, data=data)
        return schedule
    except NotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    except NotAllowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Principal cannot access other schools",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@schedules_router.get(
    "/",
    response_model=list[ScheduleDataOut],
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
def get_schedules_today(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    school_id: int | None = None,
    group_id: int | None = None,
    teacher_id: int | None = None,
) -> list[Schedule]:
    try:
        schedules = ScheduleCRUD.get_schedule_today(
            db=db,
            user=user,
            school_id=school_id,
            group_id=group_id,
            teacher_id=teacher_id,
        )
        return schedules
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="schedules not found"
        )
    except NotAllowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Principal cannot access 'school_id' query parameter",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@schedules_router.get(
    "/{schedule_id}",
    response_model=ScheduleDataOut,
    dependencies=[Depends(check_role(UserTypes.admin))],
)
def get_schedule(db: Annotated[Session, Depends(get_db)], schedule_id: int) -> Schedule:
    try:
        schedule = ScheduleCRUD.get_schedule_id(db=db, schedule_id=schedule_id)
        return schedule
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="schedules not found"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@schedules_router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))],
)
def delete_schedule(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    schedule_id: int,
) -> None:
    try:
        ScheduleCRUD.delete_schedule(db=db, user=user, schedule_id=schedule_id)
        logger.debug("Schedule with id {schedule_id} was deleted")
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="schedule not found"
        )
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Cannot delete: related records exist"
        )
    except NotAllowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Principal cannot access other schools",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@schedules_router.patch(
    "/{schedule_id}",
    response_model=ScheduleDataOut,
    dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))],
)
def update_schedule(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    schedule_id: int,
    data: ScheduleUpdateData,
) -> Schedule:
    try:
        updated_schedule = ScheduleCRUD.update_schedule(
            db=db, user=user, schedule_id=schedule_id, data=data
        )
        return updated_schedule
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't update data. Please check data validity",
        )
    except NotAllowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Principal cannot access other schools",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
