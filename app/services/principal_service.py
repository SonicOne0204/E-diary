from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.db.models.schools import School
from app.db.models.groups import Group
from app.db.models.types import Teacher, Student
from app.db.models.users import User
from app.db.models.subjects import Subject
from app.db.models.associations import subject_teacher
from app.exceptions.teachers import TeacherNotFound, TeacherAlreadyAssigned, TeacherNotInTable
from app.exceptions.students import StudentNotFound, StudentAlreadyAssigned, StudentNotInTable
from app.exceptions.subject import SubjectNotFound
from app.exceptions.basic import AlreadyExistsError
from app.schemas.principals import AssignStudentByIdSchoolModel, AssignTeacherByIdSchoolModel, AssingStudentByIdGroupModel, AssingTeacherByIdSubjectModel

import logging
logger = logging.getLogger(__name__)

class PrincipalService():
    @staticmethod
    def link_teacher_to_school_id(db: Session, school_id: int , teacher_int: int) -> Teacher:
        userside_teacher = db.query(User).get(teacher_int)
        if userside_teacher == None:
            raise TeacherNotFound()
        if userside_teacher.type != 'teacher':
            raise TeacherNotFound()
        teacher = db.query(Teacher).filter(Teacher.id == userside_teacher.id).one_or_none()
        if teacher == None:
            raise TeacherNotInTable(teacher_id=userside_teacher.id)
        if teacher.school_id != None:
            raise TeacherAlreadyAssigned(teacher_id=teacher.id, school_id=teacher.school_id)
        teacher.school_id = school_id
        try:
            db.commit()
            db.refresh(teacher)
            return teacher
        except IntegrityError:
            db.rollback()
            raise
    @staticmethod
    def link_student_to_school_id(db: Session, school_id: int, student_id: str):
        userside_student = db.query(User).get(student_id)
        if userside_student == None:
            raise StudentNotFound()
        if userside_student.type != 'student':
            raise StudentNotFound()
        student = db.query(Student).get(userside_student.id)
        if student == None:
            raise StudentNotInTable(student_id=userside_student.id)
        if student.school_id != None:
            raise StudentAlreadyAssigned(student_id=student.id, school_id=student.school_id)
        student.school_id = school_id
        try:
            db.commit()
            db.refresh(student)
            return student
        except IntegrityError:
            db.rollback()
            raise

    @staticmethod
    def link_student_to_group_id(db: Session, group_id: int, student_id: int):
        userside_student = db.query(User).get(student_id)
        if userside_student == None:
            raise StudentNotFound()
        if userside_student.type != 'student':
            raise StudentNotFound()
        student = db.query(Student).get(userside_student.id)
        if student == None:
            raise StudentNotInTable(student_id=userside_student.id)
        if student.group_id != None:
            raise StudentAlreadyAssigned(student_id=student.id, group_id=student.group_id)
        student.group_id = group_id
        try:
            db.commit()
            db.refresh(student)
            return student
        except IntegrityError:
            db.rollback()
            raise
    @staticmethod
    def link_teacher_to_subject_id(db: Session, teacher_id: int, subject_id: int):
        subject: Subject = db.query(Subject).get(subject_id)
        teacher: Teacher = db.query(User).get(teacher_id)
        if teacher == None:
            raise TeacherNotFound()
        if teacher.type != 'teacher':
            raise TeacherNotFound('User is not teacher')
        if subject == None:
            raise SubjectNotFound()
        try:
            db.execute(
                subject_teacher.insert().values(teacher_id=teacher.id, subject_id=subject.id)
            )
            db.commit() 
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error in DB: {e}')
            raise
        

    
