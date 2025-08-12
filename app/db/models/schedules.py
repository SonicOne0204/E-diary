from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime, Time
from datetime import datetime, time, timezone

from app.db.core import Base
from app.db.models.types import Teacher
from app.db.models.schools import School
from app.db.models.groups import Group
from app.db.models.subjects import Subject


class Schedule(Base):
    __tablename__ = "schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE")
    )
    school_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("schools.id", ondelete="CASCADE")
    )
    subject_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True
    )
    day_of_week: Mapped[str] = mapped_column(String)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(tz=timezone.utc)
    )
    ended_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    group: Mapped["Group"] = relationship("Group", back_populates="schedule")
    school: Mapped["School"] = relationship("School", back_populates="schedules")
    subject: Mapped["Subject"] = relationship("Subject", back_populates="schedules")
    teacher: Mapped["Teacher"] = relationship("Teacher", back_populates="schedules")
    attendance: Mapped["Attendance"] = relationship(
        "Attendance", back_populates="schedule", uselist=False
    )
    grades: Mapped[list["Grade"]] = relationship("Grade", back_populates="schedule")
