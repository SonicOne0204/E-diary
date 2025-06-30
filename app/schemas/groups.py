from pydantic import BaseModel

class GroupData(BaseModel):
    grade: int
    grade_section: str
    school_id: int