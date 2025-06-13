from enum import Enum

class Types(str, Enum):
    admin = 'admin'
    teacher = 'teacher'
    student = 'student'
    principal = 'principal'
