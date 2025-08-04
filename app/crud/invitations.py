from sqlalchemy.orm import Session

from app.db.models.users import User
from app.db.models.invitations import Invitation

from app.exceptions.basic import NotAllowed, NotFound

import logging
logger = logging.getLogger(__name__)

def get_invitations(db: Session, user: User):
    try:
        invitations: list[Invitation] = db.query(Invitation).filter(Invitation.invited_user_id == user.id).all()
        return invitations
    except Exception as e:
        logger.exception(f'Unexpected error occured: {e}')
        raise