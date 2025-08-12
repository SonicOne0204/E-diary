class TeacherAlreadyAssigned(Exception):
    def __init__(self, teacher_id: int, school_id: int):
        message = (
            f"teacher with id {teacher_id} already assinged to school with {school_id}"
        )
        super().__init__(message)


class TeacherNotInTable(Exception):
    def __init__(self, teacher_id: int):
        message = (
            f"teacher with id {teacher_id} is in users table but not in teachers table"
        )
        super().__init__(message)
