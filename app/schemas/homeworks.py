from pydantic import BaseModel
from datetime import datetime

class HomeworkData(BaseModel):
    name: str 
    description: str | None = None
    due_date: datetime 
    group_id: int
    school_id: int
    teacher_id: int

class HomeworkDataUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    group_id: int| None = None
    teacher_id: int| None = None