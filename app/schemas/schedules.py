from pydantic import BaseModel
from enum import Enum
from datetime import time, datetime

class Week(str, Enum):
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = 'wednesday'
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'
    sunday = 'sunday'

class ScheduleData(BaseModel):
    day_of_week: Week
    start_time: time
    end_time: time
    group_id: int
    school_id: int
    subject_id: int
    teacher_id: int | None = None

class ScheduleUpdateData(BaseModel):
    day_of_week: Week | None = None
    start_time: time | None = None
    end_time: time | None = None
    group_id: int | None = None
    subject_id: int | None = None
    teacher_id: int | None = None