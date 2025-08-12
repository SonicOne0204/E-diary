from pydantic import BaseModel
from enum import Enum


class GradeSystems(str, Enum):
    letter_sys = "letter"
    GPA_sys = "GPA"
    percent_sys = "percent"
    pass_fail_sys = "pass/fail"
    five_num_sys = "5numerical"


class AssignGradeData(BaseModel):
    grade_system: GradeSystems | None = None
    value_letter: str | None = None
    value_numeric: float | None = None
    value_boolean: bool | None = None
    schedule_id: int
    student_id: int


class GradeDataOut(BaseModel):
    id: int
    grade_system: GradeSystems | None = None
    value_letter: str | None = None
    value_percent: float | None = None
    value_GPA: float | None = None
    value_5numerical: int | None = None
    value_boolean: bool | None = None
    schedule_id: int
    student_id: int
    marked_by: int | None = None

    class Config:
        from_attributes = True
