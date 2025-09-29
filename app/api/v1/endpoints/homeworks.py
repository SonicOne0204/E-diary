from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from app.crud.homeworks import HomeworkCRUD
from app.db.core import get_async_db
from app.schemas.homeworks import HomeworkData, HomeworkDataUpdate, HomeworkDataOut
from app.db.models.homeworks import Homework
from app.db.models.users import User
from app.exceptions.basic import NotFound, NotAllowed
from app.dependecies.auth import check_role, get_current_user
from app.schemas.auth import UserTypes

import logging

logger = logging.getLogger(__name__)

homeworks_router = APIRouter(prefix="/homeworks", tags=["homeworks"])


@homeworks_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=HomeworkDataOut,
    dependencies=[Depends(check_role([UserTypes.admin, UserTypes.teacher]))],
)
async def add_homework(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    data: HomeworkData,
) -> Homework:
    try:
        homework: Homework = await HomeworkCRUD.add_homework(
            db=db, user=user, data=data
        )
        return homework
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No such school with id {data.school_id}",
        )
    except NotAllowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to give homework"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@homeworks_router.get(
    "/",
    response_model=list[HomeworkDataOut],
    dependencies=[
        Depends(
            check_role(
                [
                    UserTypes.admin,
                    UserTypes.teacher,
                    UserTypes.principal,
                    UserTypes.student,
                ]
            )
        )
    ],
)
async def get_homeworks(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    school_id: int,
    group_id: int | None = None,
    teacher_id: int | None = None,
) -> list[Homework]:
    try:
        homeworks: list[Homework] = await HomeworkCRUD.get_homeworks_id(
            db=db,
            user=user,
            school_id=school_id,
            group_id=group_id,
            teacher_id=teacher_id,
        )
        return homeworks
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="homeworks not found"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@homeworks_router.get("/{homework_id}/", response_model=HomeworkDataOut)
async def get_homework(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    homework_id: int,
) -> Homework:
    try:
        homework = await HomeworkCRUD.get_homework_id(
            db=db, user=user, homework_id=homework_id
        )
        return homework
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@homeworks_router.delete("/{homework_id}/")
async def delete_homework(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    homework_id: int,
) -> None:
    try:
        await HomeworkCRUD.delete_homework(db=db, user=user, homework_id=homework_id)
        logger.debug(f"Homework with id {homework_id} was deleted")
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="homework not found"
        )
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Cannot delete: related records exist"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@homeworks_router.patch("/{homework_id}/", response_model=HomeworkDataOut)
async def update_homework(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    homework_id: int,
    data: HomeworkDataUpdate,
) -> Homework:
    try:
        updated_homework = await HomeworkCRUD.update_homework(
            db=db, user=user, homework_id=homework_id, data=data
        )
        return updated_homework
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't update data. Please check data validity",
        )
    except NotAllowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to give homework"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
