from enum import Enum

class Invitation_status(str, Enum):
    pending = 'pending'
    accepted = 'accepted'
    rejected = 'rejected'