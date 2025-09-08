from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.crud.invitations import get_invitations
from app.db.core import get_async_db
from app.db.models.users import User
from app.db.models.invitations import Invitation
from app.schemas.invitations import InvitationOut
from app.dependecies.auth import get_current_user

import logging

logger = logging.getLogger(__name__)

invitations_router = APIRouter(prefix="/invitations", tags=["invitations"])


@invitations_router.get("/", response_model=InvitationOut)
async def get_invitations_by_user(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[Invitation]:
    try:
        invitations: list[Invitation] = await get_invitations(db=db, user=user)
        return invitations
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
