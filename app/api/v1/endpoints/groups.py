from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import Annotated

from app.crud.groups import GroupCRUD
from app.db.core import get_async_db
from app.schemas.groups import GroupData, GroupDataOut
from app.schemas.users import UserTypes
from app.db.models.groups import Group
from app.exceptions.basic import NotFound
from app.db.models.users import User
from app.services.auth import get_current_user
from app.dependecies.auth import check_role

import logging

logger = logging.getLogger(__name__)

groups_router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    dependencies=[Depends(check_role([UserTypes.admin, UserTypes.principal]))],
)


@groups_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=GroupDataOut
)
async def add_group(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    data: GroupData,
) -> Group:
    try:
        group = await GroupCRUD.add_group(db=db, user=user, data=data)
        return group
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="No such school"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@groups_router.get("/schools/{school_id}/", response_model=list[GroupDataOut])
async def get_groups(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    school_id: int,
) -> list[Group]:
    try:
        groups: list[Group] = await GroupCRUD.get_groups(
            db=db, user=user, school_id=school_id
        )
        return groups
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Groups not found"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@groups_router.get("/{group_id}/", response_model=GroupDataOut)
async def get_group(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    group_id: int,
) -> Group:
    try:
        group = await GroupCRUD.get_group(db=db, user=user, group_id=group_id)
        return group
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="No such school"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@groups_router.delete("/{group_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    group_id: int,
) -> None:
    try:
        await GroupCRUD.delete_group(db=db, user=user, group_id=group_id)
        logger.debug(f"Group with id {group_id} was deleted")
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Group not found"
        )
    except IntegrityError:
        raise HTTPException(
            status_code=400, detail="Cannot delete: related records exist"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@groups_router.patch("/{group_id}/", response_model=GroupDataOut)
async def update_group(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
    group_id: int,
    data: GroupData,
) -> Group:
    try:
        updated_group = await GroupCRUD.update_group(
            db=db, user=user, group_id=group_id, data=data
        )
        return updated_group
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't update data. Please check data validity",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
