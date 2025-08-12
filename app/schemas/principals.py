from pydantic import BaseModel


class InviteTeacherByIdSchoolModel(BaseModel):
    school_id: int
    teacher_id: int


class InviteStudentByIdSchoolModel(BaseModel):
    school_id: int
    student_id: int


class AssingStudentByIdGroupModel(BaseModel):
    group_id: int
    student_id: int


class AssingTeacherByIdSubjectModel(BaseModel):
    subject_id: int
    teacher_id: int
