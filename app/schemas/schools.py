from pydantic import BaseModel

class SchoolData(BaseModel):
    name: str
    short_name:str | None = None
    address: str
    country: str
    is_active: bool = True


class SchoolOut(SchoolData):
    id: int
    name: str
    is_active: bool
    address: str
    country: str
     
    class Config:
        from_attributes = True

class SchoolUpdate(BaseModel):
    name: str | None = None
    short_name:str | None = None
    address: str | None = None
    country: str | None = None
    is_active: bool = True

class SchoolUpdateOut(SchoolUpdate):
    id: int
    name: str
    is_active: bool
    address: str
    country: str

    class Config:
        form_attributes = True