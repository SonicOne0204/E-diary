from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends

from app.db.core import get_db
from app.db.models.invitations import Invitation
from app.db.models.users import User
from app.services.auth import get_current_user


def get_invitations(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> list[Invitation]:
    invitations = db.query(Invitation).filter(Invitation.invited_user_id == user.id)
    return invitations.all()
