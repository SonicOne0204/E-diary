from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime, Float, UniqueConstraint
from datetime import datetime, date, timezone

from app.db.core import Base
from app.db.models.types import Student, Teacher
from app.db.models.schedules import Schedule



class Grade(Base):
    __tablename__ = 'grades'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade_system: Mapped[str] = mapped_column(String)
    value_letter: Mapped[str] = mapped_column(String, nullable=True)
    value_percent: Mapped[float] = mapped_column(Float, nullable=True)
    value_GPA: Mapped[float] = mapped_column(Float, nullable=True)
    value_passing: Mapped[bool] = mapped_column(Boolean, nullable=True)
    value_5numerical: Mapped[Integer] = mapped_column(Integer, nullable=True)
    schedule_id: Mapped[int] = mapped_column(Integer, ForeignKey('schedules.id', ondelete='CASCADE'))
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey('students.id', ondelete='CASCADE'))
    marked_by: Mapped[int] = mapped_column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    student: Mapped['Student'] = relationship('Student', back_populates='grades')
    schedule: Mapped['Schedule'] = relationship('Schedule', back_populates='grades')
    teacher: Mapped['Teacher'] = relationship('Teacher', back_populates='grades')

    __table_args__ = (
        UniqueConstraint('schedule_id', 'student_id', name='uniqueconst_schedule_student'),
    )