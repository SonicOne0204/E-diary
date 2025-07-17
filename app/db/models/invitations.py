from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime
from datetime import datetime, timezone

from app.db.core import model
from app.db.models.schools import School

class Invitation(model):
    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(primary_key=True)
    invited_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    invited_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"))
    status: Mapped[str] = mapped_column(default="pending")
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(tz=timezone.utc))

    school: Mapped["School"] = relationship("School", back_populates="invitations")

    inviter: Mapped["User"] = relationship(
        "User",
        foreign_keys=[invited_by_id],
        back_populates="invitations_sent"
    )

    invitee: Mapped["User"] = relationship(
        "User",
        foreign_keys=[invited_user_id],
        back_populates="invitations_received"
    )
