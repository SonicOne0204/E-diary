from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from jose import jwt

from app.core.settings import settings
from app.schemas.users import UserTypes
from app.db.models.users import User
from app.services.auth import get_current_user
from app.exceptions.auth import RoleNotAllowed

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

def check_role(required_role: UserTypes):
    def role_checker(user: Annotated[User, Depends(get_current_user)]):
        if user.type == required_role:
            return user
        raise RoleNotAllowed(f'Role {user.type} is not allowed here')
    return role_checker