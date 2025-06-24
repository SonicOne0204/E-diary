from enum import Enum

class UserType(str, Enum):
    admin = 'admin'
    teacher = 'teacher'
    student = 'student'
    principal = 'principal'