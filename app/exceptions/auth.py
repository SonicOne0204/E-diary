from app.schemas.users import UserTypes

class RoleNotAllowed(Exception):
    pass
        
class UserExists(Exception):
    pass

class UserDoesNotExist(Exception):
    pass

class WrongPassword(Exception):
    pass