from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime
from datetime import datetime

from app.db.core import model
from app.db.models.types import Teacher
from app.db.models.schools import School
from app.db.models.groups import Group



class Homework(model):
    __tablename__ = 'homeworks'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String, nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups.id', ondelete='CASCADE'))
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id', ondelete='CASCADE'))
    teacher_id: Mapped[int] = mapped_column(Integer, ForeignKey('teachers.id', ondelete='CASCADE'))

    group: Mapped['Group'] = relationship('Group', back_populates='homeworks')
    teacher: Mapped['Teacher'] = relationship('Teacher', back_populates='homeworks')
    school: Mapped['School'] = relationship('School', back_populates='homeworks') 