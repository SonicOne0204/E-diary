from pydantic import BaseModel

from app.schemas.attendance import StatusOptions


class MarkPresenceData(BaseModel):
    student_id: int
    lesson_id: int
    status: StatusOptions
    teacher_id: int | None = None
