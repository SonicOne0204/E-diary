class SubjectNotFound(Exception):
    def __init__(self):
        message = 'Subjects not found'
        super().__init__(message)