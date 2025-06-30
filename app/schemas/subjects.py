from pydantic import BaseModel

class SubjectData(BaseModel):
    name: str
    school_id: int


class SubjectUpdate(BaseModel):
    name: str | None = None
    school_id: int | None = None

class SubjectDataOut(BaseModel):
    id: int
    name: str
    school_id: int


class SubjectUpdateOut(BaseModel):
    id: int
    name: str | None = None
    school_id: int | None = None