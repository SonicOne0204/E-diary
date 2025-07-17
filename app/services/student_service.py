from sqlalchemy.orm import Session

from app.db.models.types import Student
from app.exceptions.basic import NoDataError, NotFound, NotAllowed
from app.schemas.invitations import Invitation_status
from app.dependecies.invitations import get_invitations
from app.db.models.users import User
from app.db.models.invitations import Invitation

import logging
logger = logging.getLogger(__name__)

class StudentService():
    @staticmethod
    def accept_invitation(db: Session, user: User , invitation_id: int):
        try:
            invitation: Invitation = db.query(Invitation).get(invitation_id)
            if invitation_id == None:
                logger.info(f'Invitation with id {invitation_id} not found')
                raise NotFound('Invitation not found')
            if invitation.invited_user_id != user.id:
                raise NotAllowed('Cannot accept another user\'s invitation')
            logger.info(f'User with id {user.id} accepted invitation sent by user with id{invitation.invited_by_id} to school with id {invitation.school_id}')
            invitation.status = Invitation_status.accepted
            student: Student = db.query(Student).get(user.id)
            if student == None:
                logger.info(f'Student with id {user.id} is not found')
                raise NotFound('Student not found')
            student.school_id = invitation.school_id
            db.commit()
            return {'detail': 'Invitation accepted'}
        except Exception as e:
            logging.exception(f'Unexpected error occured: {e}')
            raise