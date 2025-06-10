from app.db.core import model
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey

class Group(model):
    __tablename__ = 'groups'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grade: Mapped[int] = mapped_column(Integer) 
    grade_section: Mapped[str] = mapped_column(String) # Like '10th grade, section A,B,C'
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id', ondelete='CASCADE'))

    school_group: Mapped['School'] = relationship('School', back_populates='groups') # type: ignore