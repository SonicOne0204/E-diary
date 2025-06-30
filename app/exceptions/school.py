class SchoolNotFound(Exception):
    def __init__(self, school_id):
        self.message = f'School with id {school_id} is not found'
        super().__init__(self.message)