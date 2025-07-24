from app.schemas.users import UserTypes

class RoleNotAllowed(Exception):
    def __init__(self, roles: list[UserTypes]):
        self.roles = roles
        role_names = ', '.join(role for role in roles)  # If UserTypes is an Enum
        super().__init__(f"Roles not allowed: {role_names}")

        
class UserExists(Exception):
    pass

class UserDoesNotExist(Exception):
    pass

class WrongPassword(Exception):
    pass