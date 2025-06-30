class RoleNotAllowed(Exception):
    def __init__(self):
        self.message = 'Cannot register as admin'
        super().__init__(self.message)
        
class UserExists(Exception):
    def __init__(self):
        self.message = 'User already exists'
        super().__init__(self.message)