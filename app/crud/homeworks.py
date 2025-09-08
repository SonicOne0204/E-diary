from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime

from app.schemas.homeworks import HomeworkData, HomeworkDataUpdate
from app.schemas.users import UserTypes
from app.db.models.homeworks import Homework
from app.db.models.groups import Group
from app.db.models.types import Teacher, Student, Principal
from app.db.models.users import User
from app.exceptions.basic import NotAllowed, NotFound

import logging

logger = logging.getLogger(__name__)


class HomeworkCRUD:
    @staticmethod
    async def add_homework(db: AsyncSession, user: User, data: HomeworkData):
        try:
            group = await db.get(Group, data.group_id)
            teacher = await db.get(Teacher, user.id)

            if group.school_id != data.school_id:
                raise NotAllowed("Not allowed to give homework to other schools")
            if teacher.school_id != data.school_id:
                raise NotAllowed("Not allowed to give homework to other schools")

            homework = Homework()
            data_dict = data.model_dump(exclude={"due_date"})
            if isinstance(data.due_date, str):
                parsed_dt = datetime.fromisoformat(data.due_date)
            else:
                parsed_dt = data.due_date
            homework.due_date = parsed_dt.replace(second=0, microsecond=0)

            for key, value in data_dict.items():
                setattr(homework, key, value)

            db.add(homework)
            await db.commit()
            await db.refresh(homework)
            return homework
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"DB error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise

    @staticmethod
    async def delete_homework(db: AsyncSession, user: User, homework_id: int):
        try:
            homework = await db.get(Homework, homework_id)
            if not homework:
                raise NotFound(f"Homework with id {homework_id} not found")

            if user.type == UserTypes.teacher:
                teacher = await db.get(Teacher, user.id)
                if teacher.school_id != homework.school_id:
                    raise NotAllowed("Cannot access other schools")
            elif user.type == UserTypes.principal:
                principal = await db.get(Principal, user.id)
                if principal.school_id != homework.school_id:
                    raise NotAllowed("Cannot access other schools")

            await db.delete(homework)
            await db.commit()
            return homework
        except SQLAlchemyError as e:
            logger.error(f"DB error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise

    @staticmethod
    async def update_homework(db: AsyncSession, user: User, homework_id: int, data: HomeworkDataUpdate):
        try:
            homework = await db.get(Homework, homework_id)
            if not homework:
                raise NotFound("Homework not found")

            group = await db.get(Group, data.group_id)
            teacher = await db.get(Teacher, user.id)

            if group.school_id != homework.school_id:
                raise NotAllowed("Not allowed to give homework in another school")
            if teacher.school_id != homework.school_id:
                raise NotAllowed("Not allowed to give homework in another school")

            data_dict = data.model_dump(exclude={"due_date"})
            if isinstance(data.due_date, str):
                parsed_dt = datetime.fromisoformat(data.due_date)
            else:
                parsed_dt = data.due_date
            homework.due_date = parsed_dt.replace(microsecond=0, second=0)

            for key, value in data_dict.items():
                setattr(homework, key, value)

            db.add(homework)
            await db.commit()
            await db.refresh(homework)
            return homework
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"DB error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise

    @staticmethod
    async def get_homeworks_id(
        db: AsyncSession,
        user: User,
        school_id: int,
        teacher_id: int | None = None,
        group_id: int | None = None,
    ):
        try:
            stmt = select(Homework)

            if user.type == UserTypes.principal:
                principal = await db.get(Principal, user.id)
                stmt = stmt.filter(Homework.school_id == principal.school_id)
            elif user.type == UserTypes.teacher:
                teacher = await db.get(Teacher, user.id)
                stmt = stmt.filter(Homework.school_id == teacher.school_id)
            elif user.type == UserTypes.student:
                student = await db.get(Student, user.id)
                stmt = stmt.filter(Homework.school_id == student.school_id)
            else:
                stmt = stmt.filter(Homework.school_id == school_id)

            if teacher_id is not None:
                stmt = stmt.filter(Homework.teacher_id == teacher_id)
            if group_id is not None:
                stmt = stmt.filter(Homework.group_id == group_id)

            result = await db.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"DB error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise

    @staticmethod
    async def get_homework_id(db: AsyncSession, user: User, homework_id: int):
        try:
            homework = await db.get(Homework, homework_id)
            if not homework:
                raise NotFound("Homework not found")

            if user.type == UserTypes.principal:
                principal = await db.get(Principal, user.id)
                if homework.school_id != principal.school_id:
                    raise NotAllowed("Cannot access other schools")
            elif user.type == UserTypes.teacher:
                teacher = await db.get(Teacher, user.id)
                if homework.school_id != teacher.school_id:
                    raise NotAllowed("Cannot access other schools")
            elif user.type == UserTypes.student:
                student = await db.get(Student, user.id)
                if homework.school_id != student.school_id:
                    raise NotAllowed("Cannot access other schools")

            return homework
        except SQLAlchemyError as e:
            logger.error(f"DB error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise
