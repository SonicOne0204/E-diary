from fastapi import APIRouter, Depends, status, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session

from app.db.core import get_db
from app.crud.schools import SchoolCRUD
from app.schemas.schools import SchoolData, SchoolOut, SchoolUpdate, SchoolUpdateOut
from app.exceptions.basic import NotFound, NotAllowed
from app.dependecies.auth import check_role
from app.schemas.users import UserTypes
from app.services.auth import get_current_user
from app.db.models.users import User
from app.db.models.schools import School

import logging

logger = logging.getLogger(__name__)

school_router = APIRouter(
    prefix="/schools",
    tags=["school"],
)


@school_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SchoolOut,
    dependencies=[Depends(check_role(UserTypes.admin))],
)
def add_school(db: Annotated[Session, Depends(get_db)], data: SchoolData) -> School:
    try:
        school = SchoolCRUD.create_school(db=db, data=data)
        return school
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"School name {data.name} is already used",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@school_router.get("/", response_model=dict)
def get_school(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    school_name: str | None = None,
    school_id: int | None = None,
) -> School:
    try:
        school = SchoolCRUD.get_school(
            db=db, user=user, name=school_name, school_id=school_id
        )
        return school
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="School is not found"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@school_router.patch(
    "/{school_id}",
    response_model=SchoolUpdateOut,
    dependencies=[Depends(check_role(UserTypes.admin))],
)
def update_school_data(
    db: Annotated[Session, Depends(get_db)],
    school_id: Annotated[int, Path()],
    data: SchoolUpdate,
) -> School:
    try:
        updated_school = SchoolCRUD.update_school_data(
            db=db, school_id=school_id, data=data
        )
        return updated_school
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"School with id {school_id} is not found",
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"School with name {data.name} does not exist",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@school_router.delete(
    "/{school_id}",
    response_model=bool,
    dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))],
)
def delete_school(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    school_id: Annotated[int, Path()],
) -> None:
    try:
        SchoolCRUD.delete_school(db=db, user=user, school_id=school_id)
        logger.debug(f"school with id {school_id} was deleted")
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"School with id: {school_id} is not found",
        )
    except NotAllowed as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@school_router.get(
    "/",
    response_model=list[SchoolOut],
    dependencies=[Depends(check_role(UserTypes.admin))],
)
def get_schools(
    db: Annotated[Session, Depends(get_db)],
    country: str | None = None,
    is_active: bool | None = None,
) -> list[School]:
    try:
        schools = SchoolCRUD.get_schools(db=db, country=country, is_active=is_active)
        return schools
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Schools not found"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
