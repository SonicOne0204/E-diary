from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends

from app.db.core import get_async_db  # <-- you need an async version of get_db
from app.db.models.invitations import Invitation
from app.db.models.users import User
from app.services.auth import get_current_user


async def get_invitations(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[Invitation]:
    result = await db.execute(
        select(Invitation).where(Invitation.invited_user_id == user.id)
    )
    invitations = result.scalars().all()
    return invitations
