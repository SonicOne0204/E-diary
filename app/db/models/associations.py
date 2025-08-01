from sqlalchemy import Table, ForeignKey, Integer, Column
from sqlalchemy.orm import relationship
from app.db.core import Base

subject_teacher = Table(
    'subject_teacher',
    Base.metadata,
    Column('teacher_id', Integer, ForeignKey('teachers.id'), primary_key=True),
    Column('subject_id', Integer, ForeignKey('subjects.id'), primary_key=True)
)