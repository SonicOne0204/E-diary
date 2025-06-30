class GroupNotFound(Exception):
    def __init__(self):
        self.message = 'Groups not found'
        super().__init__(self.message)

class GroupNotAllowed(Exception):
    pass