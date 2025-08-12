from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class Invitation_status(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


class InvitationOut(BaseModel):
    id: int
    invited_by_id: int
    invited_user_id: int
    school_id: int
    status: Invitation_status
    created_at: datetime
