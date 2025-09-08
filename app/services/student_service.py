from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.types import Student
from app.exceptions.basic import NotFound, NotAllowed
from app.schemas.invitations import Invitation_status
from app.db.models.users import User
from app.db.models.invitations import Invitation

import logging

logger = logging.getLogger(__name__)


class StudentService:
    @staticmethod
    async def accept_invitation(db: AsyncSession, user: User, invitation_id: int):
        try:
            invitation: Invitation | None = await db.get(Invitation, invitation_id)
            if invitation is None:
                logger.info(f"Invitation with id {invitation_id} not found")
                raise NotFound("Invitation not found")

            if invitation.invited_user_id != user.id:
                raise NotAllowed("Cannot accept another user's invitation")

            logger.info(
                f"User with id {user.id} accepted invitation sent by user with id {invitation.invited_by_id} "
                f"to school with id {invitation.school_id}"
            )

            invitation.status = Invitation_status.accepted

            student: Student | None = await db.get(Student, user.id)
            if student is None:
                logger.info(f"Student with id {user.id} is not found")
                raise NotFound("Student not found")

            student.school_id = invitation.school_id
            await db.commit()

            return {"detail": "Invitation accepted"}

        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise
