from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class Registration_data(BaseModel):
    username: str
    password: str
    role: int

class Login_data(BaseModel):
    username: str
    password: str