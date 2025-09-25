from pydantic import BaseModel, ConfigDict
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


class TeacherRegistrationData(RegistrationData):
    type: Literal[UserTypes.teacher] = UserTypes.teacher


class StudentRegistrationData(RegistrationData):
    type: Literal[UserTypes.student] = UserTypes.student


class PrincipalRegistrationData(RegistrationData):
    type: Literal[UserTypes.principal] = UserTypes.principal
    school_id: int | None = None


class RegistrationDataOut(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    type: UserTypes

    model_config = ConfigDict(from_attributes=True)


class PrincipalRegistrationDataOut(RegistrationDataOut):
    school_id: int | None = None


class LoginData(BaseModel):
    username: str
    password: str
