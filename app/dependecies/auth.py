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

def check_role(required_roles: list[UserTypes] | UserTypes):
    def role_checker(user: Annotated[User, Depends(get_current_user)]):
        if isinstance(required_roles, list):
            if user.type in required_roles :
                return user
        else:
            if user.type == required_roles:
                print(required_roles)
                return user
        raise RoleNotAllowed(user.type)
    return role_checker