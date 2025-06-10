from sqlalchemy import String, Integer, Sequence, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.db.core import model
from app.db.models.users import User

# Teacher, Student inherit from User model, because it is filled through polymorphysm 

class Teacher(User):
    __tablename__ = 'teachers'
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'))
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id'))

    school: Mapped['School'] = relationship('School', back_populates='teachers') # type:ignore
    role: Mapped['Role'] = relationship('Role', back_populates='users') # type: ignore

    __mapper_args__ = {
        'polymorhic_identity': 'teacher'
    }