from sqlalchemy import String, Integer, Sequence, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.db.core import model
from app.db.models.users import User
from app.db.models.schools import School
from app.db.models.roles import Role
from app.db.models.groups import Group

# Teacher, Student inherit from User model, because it is filled through polymorphysm 

class Teacher(User):
    __tablename__ = 'teachers'
    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=True)
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id', ondelete='CASCADE'), nullable=True)

    school: Mapped['School'] = relationship('School', back_populates='teachers', passive_deletes=True) 
    role: Mapped['Role'] = relationship('Role', back_populates='teachers', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'teacher'
    }

class Principal(User):
    __tablename__ = 'principals'

    id: Mapped[int] = mapped_column(Integer,ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id', ondelete='CASCADE'), nullable=True)

    school: Mapped['School'] = relationship('School', back_populates='principals', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'principal'
    }


class Student(User):
    __tablename__ = 'students'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id', ondelete='CASCADE'), nullable=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups.id', ondelete='CASCADE'), nullable=True)

    school: Mapped['School'] = relationship('School',back_populates='students',passive_deletes=True)
    group: Mapped['Group'] = relationship('Group', back_populates='students', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }
