from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey

from app.db.core import model
from app.db.models.schools import School
from app.db.models.associations import subject_teacher

class Subject(model):
    __tablename__ = 'subjects'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id', ondelete='CASCADE'))

    homeworks: Mapped[list['Homework']] = relationship('Homework', back_populates='subjects', passive_deletes=True)
    teachers: Mapped[list['Teacher']] = relationship('Teacher', back_populates='subjects', secondary=subject_teacher)
    school: Mapped['School'] = relationship('School', back_populates='subjects', passive_deletes=True)