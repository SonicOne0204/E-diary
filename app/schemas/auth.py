from pydantic import BaseModel, Field
from enum import Enum

class User_type(str, Enum):
    admin = 'admin'
    teacher = 'teacher'
    student = 'student'


class Token(BaseModel):
    access_token: str
    token_type: str

class Registration_data(BaseModel):
    username: str
    password: str
    type: User_type

class Login_data(BaseModel):
    username: str
    password: str