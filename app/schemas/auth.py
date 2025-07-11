from pydantic import BaseModel, Field
from app.schemas.users import UserTypes
from typing import Literal

class Token(BaseModel):
    access_token: str
    token_type: str

class RegistrationData(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    type: UserTypes

class TeacherRegistrationData(RegistrationData):
    type: Literal['teacher']
    role_id: int | None = None
    school_id: int | None = None

class StudentRegistrationData(RegistrationData):
    type: Literal['student']
    school_id: int | None = None
    group_id: int | None = None

class PrincipalRegistrationData(RegistrationData):
    type: Literal['principal']
    school_id: int | None = None


class LoginData(BaseModel):
    username: str
    password: str