from app.schemas.users import UserTypes

class RoleNotAllowed(Exception):
    def __init__(self, role: UserTypes):
        self.role = role
        super().__init__(f'Role {self.role} is not allowed')
        
class UserExists(Exception):
    pass

class UserDoesNotExist(Exception):
    pass