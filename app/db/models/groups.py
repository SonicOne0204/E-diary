from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey

from app.db.core import model
from app.db.models.schools import School

class Group(model):
    __tablename__ = 'groups'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade: Mapped[int] = mapped_column(Integer) 
    grade_section: Mapped[str] = mapped_column(String) # Like '10th grade, section A,B,C'
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id', ondelete='CASCADE'))

    homeworks: Mapped[list['Homework']] = relationship('Homework', back_populates='group', passive_deletes=True)
    school: Mapped['School'] = relationship('School', back_populates='groups', passive_deletes=True) 
    students: Mapped[list['Student']] = relationship('Student', back_populates='group', passive_deletes=True)# type: ignore