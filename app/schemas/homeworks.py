from pydantic import BaseModel
from datetime import datetime


class HomeworkData(BaseModel):
    name: str
    description: str | None = None
    due_date: datetime
    subject_id: int
    group_id: int
    school_id: int


class HomeworkDataOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    due_date: datetime
    subject_id: int
    group_id: int
    school_id: int


class HomeworkDataUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    subject_id: int | None = None
    group_id: int | None = None
    teacher_id: int | None = None
