from sqlalchemy.orm import Session

from app.db.models.users import User
from app.db.models.grades import Grade
from app.schemas.users import UserTypes
from app.exceptions.auth import RoleNotAllowed

import logging

logger = logging.getLogger(__name__)


def sort_grades(student_grades: list[Grade]):
    grades_percent = []
    grades_GPA = []
    grades_5numeric = []
    grades_passing = []
    grades_letter = []

    for student_grade in student_grades:
        if student_grade.value_percent != None:
            grades_percent.append(student_grade.value_percent)
        elif student_grade.value_GPA != None:
            grades_GPA.append(student_grade.value_GPA)
        elif student_grade.value_5numerical != None:
            grades_5numeric.append(student_grade.value_5numerical)
        elif student_grade.value_passing != None:
            grades_passing.append(student_grade.value_passing)
        elif student_grade.value_letter != None:
            grades_letter.append(student_grade.value_letter)
    sorted_grades = []
    if grades_percent:
        sorted_grades.append(grades_percent)
    if grades_GPA:
        sorted_grades.append(grades_GPA)
    if grades_5numeric:
        sorted_grades.append(grades_5numeric)
    if grades_passing:
        sorted_grades.append(grades_passing)
    if grades_letter:
        sorted_grades.append(grades_letter)

    return sorted_grades


class GradeService:
    def __init__(self, db: Session, student: User):
        if student.type != UserTypes.student:
            raise RoleNotAllowed(
                [UserTypes.admin, UserTypes.principal, UserTypes.teacher]
            )
        grades_raw = db.query(Grade).filter(Grade.student_id == student.id).all()
        self.grades = sort_grades(grades_raw)
        self.user = student

    def avarege(self):
        unawaiable_grades = ["grades_passing", "grades_letter"]
        for grade in self.grades:
            if grade in unawaiable_grades:
                logger.debug(
                    f'Skipped "{grade}" of student {self.user}. Cannot average booleans or strings'
                )
                continue
            average = grade / len(self.grades)
            sum = {}
            sum[grade] = average
            return sum
