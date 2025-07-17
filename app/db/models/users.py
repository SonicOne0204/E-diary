from sqlalchemy import String, Integer, Sequence, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.db.core import model 
from app.db.models.invitations import Invitation

class User(model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)

    invitations_sent: Mapped[list["Invitation"]] = relationship(
        "Invitation",
        back_populates="inviter",
        foreign_keys=[Invitation.invited_by_id]
    )

    invitations_received: Mapped[list["Invitation"]] = relationship(
        "Invitation",
        back_populates="invitee",
        foreign_keys=[Invitation.invited_user_id]
    )

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
        'polymorphic_on': type
    }



