class AlreadyExistsError(Exception):
    def __init__(self):
        self.message = 'This data already exists'
        super().__init__(self.message)

class NoDataError(Exception):
    pass