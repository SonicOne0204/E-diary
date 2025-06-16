from enum import Enum
from pydantic import BaseModel
class Types(str, Enum):
    admin = 'admin'
    teacher = 'teacher'
    student = 'student'
    principal = 'principal'


