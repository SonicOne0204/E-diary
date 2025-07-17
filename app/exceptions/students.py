

class StudentAlreadyAssigned(Exception):
    def __init__(self, student_id: int, school_id: int | None = None, group_id: int | None = None):
        if school_id:
            message = f'Student with id {student_id} already assinged to school with {school_id}'
        if group_id:
            message = f'Student with id {student_id} already assinged to group with {group_id}'
        super().__init__(message)

class StudentNotInTable(Exception):
    def __init__(self, student_id: int):
        message = f'Student with id {student_id} is in users table but not in students table'
        super().__init__(message)