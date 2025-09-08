from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.users import User
from app.db.models.invitations import Invitation

import logging

logger = logging.getLogger(__name__)


async def get_invitations(db: AsyncSession, user: User):
    try:
        stmt = select(Invitation).filter(Invitation.invited_user_id == user.id)
        result = await db.execute(stmt)
        invitations: list[Invitation] = result.scalars().all()
        return invitations
    except Exception as e:
        logger.exception(f"Unexpected error occured: {e}")
        raise
