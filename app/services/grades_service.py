from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.users import User
from app.db.models.types import Student
from app.db.models.grades import Grade
from app.schemas.users import UserTypes
from app.exceptions.auth import RoleNotAllowed
from app.exceptions.basic import NotAllowed, NotFound, NoDataError

import logging

logger = logging.getLogger(__name__)


async def sort_grades(student_grades: list[Grade]):
    grades_percent = ["percent"]
    grades_GPA = ["GPA"]
    grades_5numeric = ["5numeric"]
    grades_passing = ["passing"]
    grades_letter = ["letter"]

    for student_grade in student_grades:
        if student_grade.value_percent is not None:
            grades_percent.append(student_grade.value_percent)
        elif student_grade.value_GPA is not None:
            grades_GPA.append(student_grade.value_GPA)
        elif student_grade.value_5numerical is not None:
            grades_5numeric.append(student_grade.value_5numerical)
        elif student_grade.value_passing is not None:
            grades_passing.append(student_grade.value_passing)
        elif student_grade.value_letter is not None:
            grades_letter.append(student_grade.value_letter)

    sorted_grades = []
    if len(grades_percent) > 1:
        sorted_grades.append(grades_percent)
    if len(grades_GPA) > 1:
        sorted_grades.append(grades_GPA)
    if len(grades_5numeric) > 1:
        sorted_grades.append(grades_5numeric)
    if len(grades_passing) > 1:
        sorted_grades.append(grades_passing)
    if len(grades_letter) > 1:
        sorted_grades.append(grades_letter)

    return sorted_grades


class GradeService:
    def __init__(self, grades, student: Student):
        self.grades = grades
        self.user = student # Can possibly use later 

    @classmethod
    async def create(cls, db: AsyncSession, user: User, student_id: int):
        # get student
        result = await db.execute(select(Student).where(Student.id == student_id))
        student: Student | None = result.scalar_one_or_none()

        if not student:
            raise NotFound("Student not found")

        if user.type != UserTypes.admin:
            if user.school_id != student.school_id:
                raise NotAllowed("Not allowed to access other schools")

        if student.type != UserTypes.student:
            raise RoleNotAllowed(
                [UserTypes.admin, UserTypes.principal, UserTypes.teacher]
            )

        # get grades
        result = await db.execute(select(Grade).where(Grade.student_id == student.id))
        grades_raw = result.scalars().all()

        grades = await sort_grades(grades_raw)

        return cls(grades=grades, student=student)

    def average(self):
        summary = {}
        for grade in self.grades:
            if grade[0] in ("letter", "passing"):
                logger.debug(
                    f'Skipped "{grade}" of student {self.user}. Cannot average booleans or strings'
                )
                continue

            grade_type = grade.pop(0)
            if not grade:
                logger.debug(
                    f'Skipped "{grade}" of student {self.user}. Cannot average empty lists'
                )
                continue
            else:
                average = sum(grade) / len(grade)
            summary[grade_type] = average

        if not summary:
            raise NoDataError("Student doesn't have grades yet")
        return summary
