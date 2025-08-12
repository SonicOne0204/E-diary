from pydantic import BaseModel
from enum import Enum


class StatusOptions(str, Enum):
    absent = "absent"
    present = "present"
    excused = "excused"
    late = "late"


class AttendanceOut(BaseModel):
    id: int
    student_id: int
    schedule_id: int
    marked_by: int | None
    status: StatusOptions

    class Config:
        from_attributes = True
