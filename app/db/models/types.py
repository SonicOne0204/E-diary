from sqlalchemy import String, Integer, Sequence, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.db.core import Base
from app.db.models.users import User
from app.db.models.schools import School
from app.db.models.groups import Group
from app.db.models.associations import subject_teacher
# Teacher, Student inherit from User model, because it is filled through polymorphysm 

class Teacher(User):
    __tablename__ = 'teachers'
    id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey('schools.id', ondelete='CASCADE'), nullable=True)

    school: Mapped['School'] = relationship('School', back_populates='teachers', passive_deletes=True) 
    subjects: Mapped[list['Subject']] = relationship('Subject', back_populates='teachers', secondary=subject_teacher)
    homeworks: Mapped[list['Homework']] = relationship('Homework', back_populates='teacher')
    schedules: Mapped[list['Schedule']] = relationship('Schedule', back_populates='teacher')
    attendance: Mapped['Attendance'] = relationship('Attendance', back_populates='teacher')
    grades: Mapped[list['Grade']] = relationship('Grade', back_populates='teacher')

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
    attendance: Mapped['Attendance'] = relationship('Attendance', back_populates='student')
    grades: Mapped[list['Grade']] = relationship('Grade', back_populates='student')
    __mapper_args__ = {
        'polymorphic_identity': 'student'
    }
