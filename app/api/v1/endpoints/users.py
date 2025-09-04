from fastapi import APIRouter, Path, status, HTTPException, Depends, Query
from typing import Annotated
from sqlalchemy.orm import Session

from app.crud.users import UsersCRUD
from app.db.core import get_db
from app.db.models.users import User
from app.schemas.users import UserOut, UserTypes
from app.exceptions.basic import NotFound
from app.dependecies.auth import check_role


import logging

logger = logging.getLogger(__name__)

users_router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(check_role(UserTypes.admin))]
)


@users_router.get("/", response_model=list[UserOut])
async def get_users(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int | None, Query(ge=1)] = 1,
    limit: Annotated[int | None, Query(ge=1, le=50)] = 10,
    username: str | None = None,
) -> list[User]:
    try:
        return await UsersCRUD.get_users(db=db, page=page, limit=limit, username=username)
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such user"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occured",
        )


@users_router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    db: Annotated[Session, Depends(get_db)], user_id: Annotated[int, Path()]
) -> None:
    try:
        UsersCRUD.delete_user(db=db, user_id=user_id)
        logger.debug(f"User with id {user_id} was deleted")
    except NotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No such user"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occured",
        )
