from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.db.models.schools import School
from app.db.models.groups import Group
from app.db.models.types import Teacher, Student, Principal
from app.db.models.users import User
from app.db.models.subjects import Subject
from app.db.models.associations import subject_teacher
from app.db.models.invitations import Invitation
from app.exceptions.teachers import TeacherAlreadyAssigned, TeacherNotInTable
from app.exceptions.students import StudentAlreadyAssigned, StudentNotInTable
from app.exceptions.basic import AlreadyExistsError, NotFound, NotAllowed

import logging
logger = logging.getLogger(__name__)

class PrincipalService():
    @staticmethod
    def invite_teacher_to_school_id(db: Session, user: User ,school_id: int , teacher_id: int) -> Invitation:
        userside_teacher: User = db.query(User).get(teacher_id)
        if userside_teacher == None:
            logger.info(f'Teacher with id {teacher_id} is not found')
            raise NotFound('Teacher not found')
        if userside_teacher.type != 'teacher':
            logger.warning(f'User with id {teacher_id}has type not \'teacher\'')
            raise NotFound(f'This user is {userside_teacher.type}, not teacher')
        teacher: Teacher = db.query(Teacher).filter(Teacher.id == userside_teacher.id).one_or_none()
        print(type(teacher))
        if teacher == None:
            raise TeacherNotInTable(teacher_id=userside_teacher.id)
        if teacher.school_id != None:
            raise TeacherAlreadyAssigned(teacher_id=teacher.id, school_id=teacher.school_id)
        invitation = Invitation(school_id=school_id, invited_by_id=user.id, invited_user_id=teacher.id)
        try:
            db.add(invitation)
            db.commit()
            db.refresh(invitation)
            return invitation
        except IntegrityError:
            logger.error(f'Error in DB: {e}')
            db.rollback()
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error in DB: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise
    @staticmethod
    def invite_student_to_school_id(db: Session, user: User ,school_id: int , student_id: int) -> Invitation:
        try:
            userside_student: User = db.query(User).get(student_id)
            if userside_student == None:
                logger.info(f'Student with id {student_id} is not found')
                raise NotFound('Student not found')
            if userside_student.type != 'student':
                logger.warning(f'User with id {student_id}has type not \'student\'')
                raise NotFound(f'This user is {userside_student.type}, not student')
            student: Student = db.query(Student).filter(Student.id == userside_student.id).one_or_none()
            if student == None:
                raise StudentNotInTable(student_id=userside_student.id)
            if student.school_id != None:
                raise StudentAlreadyAssigned(student_id=student.id, school_id=student.school_id)
            invitation = Invitation(school_id=school_id, invited_by_id=user.id, invited_user_id=student.id)
            db.add(invitation)
            db.commit()
            db.refresh(invitation)
            return invitation
        except IntegrityError:
            db.rollback()
            logger.error(f'Error in DB: {e}')
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error in DB: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

    @staticmethod
    def link_student_to_group_id(db: Session, user: User ,group_id: int, student_id: int):
        try:
            userside_student: User = db.query(User).get(student_id)
            if userside_student == None:
                raise NotFound() 
            if userside_student.type != 'student':
                raise NotFound()
            student: Student = db.query(Student).get(userside_student.id)
            principal: Principal = db.query(Principal).get(user.id)
            group: Group = db.query(Group).get(group_id)
            if student == None:
                raise StudentNotInTable(student_id=userside_student.id)
            if student.group_id != None:
                raise StudentAlreadyAssigned(student_id=student.id, group_id=student.group_id)
            if student.school_id != principal.school_id:
                raise NotAllowed('Cannot asign students from other schools')
            if group.school_id != principal.school_id:
                raise NotAllowed('Cannot asign groups from other schools')
            student.group_id = group_id
            db.commit()
            db.refresh(student)
            return student
        except IntegrityError:
            db.rollback()
            logger.error(f'Error in DB: {e}')
            raise
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error in DB: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise
    @staticmethod
    def link_teacher_to_subject_id(db: Session, user: User , teacher_id: int, subject_id: int):
        try:
            subject: Subject = db.query(Subject).get(subject_id)
            teacher: Teacher = db.query(User).get(teacher_id)
            principal: Principal = db.query(Principal).get(user.id)
            if teacher == None:
                raise NotFound('User not found')
            if teacher.type != 'teacher':
                raise NotFound('User is not teacher')
            if subject == None:
                raise NotFound('Subject not found')
            if teacher.school_id != principal.school_id:
                raise NotAllowed('Cannot asign teachers from other schools')
            if subject.school_id != principal.school_id:
                raise NotAllowed('Cannot asign subjects from other schools')
            db.execute(subject_teacher.insert().values(teacher_id=teacher.id, subject_id=subject.id))
            db.commit() 
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f'Error in DB: {e}')
            raise
        except Exception as e:
            logger.exception(f'Unexpected error occured: {e}')
            raise

        

    
