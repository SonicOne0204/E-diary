from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from datetime import datetime, date, timezone
from fastapi import Depends
from typing import Annotated

from app.schemas.schedules import ScheduleData, ScheduleUpdateData, Week
from app.schemas.users import UserTypes
from app.exceptions.basic import NotAllowed, NotFound
from app.db.models.types import Student, Teacher, Principal
from app.db.models.schedules import Schedule
from app.db.models.attendance import Attendance
from app.db.models.groups import Group
from app.db.models.schools import School
from app.db.models.subjects import Subject
from app.db.models.users import User
from app.services.auth import get_current_user

import logging

logger = logging.getLogger(__name__)


async def create_attendance(
    db: AsyncSession,
    schedules: list[Schedule],
    school_id: int | None = None,
    group_id: int | None = None,
):
    try:
        today = date.today()
        attendances = []

        if group_id:
            stmt = select(Student).filter(Student.group_id == group_id)
        elif school_id:
            stmt = select(Student).filter(Student.school_id == school_id)
        else:
            return attendances

        result = await db.execute(stmt)
        students = result.scalars().all()

        for schedule in schedules:
            for student in students:
                stmt = (
                    select(Attendance)
                    .filter(Attendance.schedule_id == schedule.id)
                    .filter(Attendance.student_id == student.id)
                    .filter(Attendance.created_at == today)
                )
                existing = await db.execute(stmt)
                if existing.scalar_one_or_none():
                    continue

                attendance = Attendance(
                    schedule_id=schedule.id,
                    student_id=student.id,
                    created_at=today,
                )
                db.add(attendance)
                await db.commit()
                await db.refresh(attendance)
                attendances.append(attendance)

        return attendances
    except Exception as e:
        await db.rollback()
        logger.exception(f"Unexpected error occured: {e}")
        raise


class ScheduleCRUD:
    @staticmethod
    async def create_schedule(
        db: AsyncSession,
        data: ScheduleData,
        user: Annotated[User, Depends(get_current_user)],
    ):
        try:
            subject = await db.get(Subject, data.subject_id)
            teacher = await db.get(Teacher, data.teacher_id)
            group = await db.get(Group, data.group_id)
            school = await db.get(School, data.school_id)
            principal = await db.get(Principal, user.id)

            if not subject:
                raise NotFound("Subject not found")
            if not teacher:
                raise NotFound("Teacher not found")
            if not group:
                raise NotFound("Group not found")
            if not school:
                raise NotFound("School not found")

            if (
                user.type == UserTypes.principal
                and data.school_id != principal.school_id
            ):
                logger.warning(
                    f"Principal with id {principal.id} cannot assign schedule to school {school.id}"
                )
                raise NotAllowed("Cannot assign schedule to another school")

            data_dict = data.model_dump(exclude_unset=True)
            schedule = Schedule(**data_dict, created_at=datetime.now(tz=timezone.utc))
            db.add(schedule)
            await db.commit()
            await db.refresh(schedule)
            return schedule
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error occured: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occured: {e}")
            raise

    @staticmethod
    async def get_schedule_id(db: AsyncSession, schedule_id: int):
        try:
            schedule = await db.get(Schedule, schedule_id)
            if not schedule:
                raise NotFound("Schedule not found")
            return schedule
        except Exception as e:
            logger.exception(f"Unexpected error occured: {e}")
            raise

    @staticmethod
    async def get_schedule_today(
        db: AsyncSession,
        user: User,
        school_id: int | None = None,
        group_id: int | None = None,
        teacher_id: int | None = None,
    ):
        try:
            day_of_week = date.today().strftime("%A").lower()
            stmt = select(Schedule).filter(Schedule.day_of_week == day_of_week)

            user_school_id = None
            match user.type:
                case UserTypes.principal:
                    principal = await db.get(Principal, user.id)
                    user_school_id = principal.school_id
                case UserTypes.teacher:
                    teacher = await db.get(Teacher, user.id)
                    user_school_id = teacher.school_id
                case UserTypes.student:
                    student = await db.get(Student, user.id)
                    user_school_id = student.school_id

            if school_id is not None:
                if user.type != UserTypes.admin:
                    raise NotAllowed(f"{user.type} cannot access other schools")
                stmt = stmt.filter(Schedule.school_id == school_id)
            else:
                stmt = stmt.filter(Schedule.school_id == user_school_id)

            if group_id:
                stmt = stmt.filter(Schedule.group_id == group_id)
            if teacher_id:
                stmt = stmt.filter(Schedule.teacher_id == teacher_id)

            result = await db.execute(stmt)
            schedules = result.scalars().all()

            await create_attendance(
                db=db,
                schedules=schedules,
                school_id=user_school_id or school_id,
                group_id=group_id,
            )

            return schedules
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def get_schedule_day_of_week(
        db: AsyncSession,
        user: User,
        day_of_week: Week,
        school_id: int | None = None,
        group_id: int | None = None,
        teacher_id: int | None = None,
    ):
        try:
            stmt = select(Schedule).filter(Schedule.day_of_week == day_of_week)

            user_school_id = None
            match user.type:
                case UserTypes.principal:
                    principal = await db.get(Principal, user.id)
                    user_school_id = principal.school_id
                case UserTypes.teacher:
                    teacher = await db.get(Teacher, user.id)
                    user_school_id = teacher.school_id
                case UserTypes.student:
                    student = await db.get(Student, user.id)
                    user_school_id = student.school_id

            if school_id is not None:
                if user.type != UserTypes.admin:
                    raise NotAllowed(f"{user.type} cannot access other schools")
                stmt = stmt.filter(Schedule.school_id == school_id)
            else:
                stmt = stmt.filter(Schedule.school_id == user_school_id)

            if group_id:
                stmt = stmt.filter(Schedule.group_id == group_id)
            if teacher_id:
                stmt = stmt.filter(Schedule.teacher_id == teacher_id)

            result = await db.execute(stmt)
            schedules = result.scalars().all()

            await create_attendance(
                db=db,
                schedules=schedules,
                school_id=user_school_id or school_id,
                group_id=group_id,
            )

            return schedules
        except Exception as e:
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def delete_schedule(db: AsyncSession, user: User, schedule_id: int):
        try:
            schedule = await db.get(Schedule, schedule_id)
            if not schedule:
                raise NotFound("Schedule not found")

            if user.type == UserTypes.principal:
                principal = await db.get(Principal, user.id)
                if schedule.school_id != principal.school_id:
                    raise NotAllowed("Principal cannot delete schedule from other schools")

            await db.delete(schedule)
            await db.commit()
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occurred: {e}")
            raise

    @staticmethod
    async def update_schedule(
        db: AsyncSession, user: User, schedule_id: int, data: ScheduleUpdateData
    ):
        try:
            schedule = await db.get(Schedule, schedule_id)
            if not schedule:
                raise NotFound("Schedule not found")

            if user.type == UserTypes.principal:
                principal = await db.get(Principal, user.id)
                if schedule.school_id != principal.school_id:
                    raise NotAllowed("Principal cannot update schedule from other schools")

            data_dict = data.model_dump(exclude_unset=True)
            for key, value in data_dict.items():
                setattr(schedule, key, value)

            db.add(schedule)
            await db.commit()
            await db.refresh(schedule)
            return schedule
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Integrity error occured: {e}")
            raise
        except Exception as e:
            await db.rollback()
            logger.exception(f"Unexpected error occured: {e}")
            raise
