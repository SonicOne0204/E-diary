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
    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'))
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id'))

    school: Mapped['School'] = relationship('School', back_populates='teachers') 
    role: Mapped['Role'] = relationship('Role', back_populates='teachers')

    __mapper_args__ = {
        'polymorphic_identity': 'teacher'
    }

class Principal(User):
    __tablename__ = 'principals'
    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id'))

    school: Mapped['School'] = relationship('School', back_populates='principals') 

    __mapper_args__ = {
        'polymorphic_identity': 'principal'
    }

class Student(User):
    __tablename__ = 'students'
    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id'))
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups.id')) 

    school: Mapped['School'] = relationship('School', back_populates='students') 
    group: Mapped['Group'] = relationship('Group', back_populates='students')
    
    __mapper_args__={
        'polymorphic_identity': 'student'
    }