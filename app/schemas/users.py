from enum import Enum
from pydantic import BaseModel

class UserTypes(str, Enum):
    admin = 'admin'
    teacher = 'teacher'
    student = 'student'
    principal = 'principal'

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    type: str
  