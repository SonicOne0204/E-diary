from enum import Enum
from pydantic import BaseModel, EmailStr, ConfigDict


class UserTypes(str, Enum):
    admin = "admin"
    teacher = "teacher"
    student = "student"
    principal = "principal"


class UserOut(BaseModel):
    id: int
    username: str | None = None
    email: EmailStr
    first_name: str
    last_name: str
    type: str

    model_config = ConfigDict(from_attributes=True)