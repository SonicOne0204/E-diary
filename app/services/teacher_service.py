from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.models.schedules import Schedule
from app.db.models.types import Student, Teacher
from app.db.models.attendance import Attendance
from app.exceptions.schedules import ScheduleNotFound
from app.exceptions.students import StudentNotFound
from app.exceptions.teachers import TeacherNotFound
from app.schemas.attendance import StatusOptions

class TeacherService():
    @staticmethod
    def mark_presence(db: Session, student_id: int, lesson_id: int, status: StatusOptions, teacher_id: int | None = None ):
        lesson = db.query(Schedule).get(lesson_id)
        student = db.query(Student).get(student_id)
        teacher = db.query(Teacher).get(teacher_id)
        if lesson == None:
            raise ScheduleNotFound('Schedule not found')
        if student == None:
            raise StudentNotFound('Student not found')
        if teacher == None:
            raise TeacherNotFound('Teacher not found')
        
        query = db.query(Attendance).filter(Attendance.schedule_id == lesson_id)
        attendance = query.filter(Attendance.student_id == student_id).one_or_none()
        if attendance:
            attendance.status = status
            attendance.updated_at = datetime.now(tz=timezone.utc)
            attendance.marked_by = teacher_id
        else:
            if teacher_id != None:
                attendance = Attendance(status=True, student_id=student_id, marked_by=teacher_id, schedule_id=lesson_id, created_at=datetime.now())
            else:
                attendance = Attendance(status=True, student_id=student_id, schedule_id=lesson_id, created_at=datetime.now())
            db.add(attendance)
        db.commit()
        return attendance
