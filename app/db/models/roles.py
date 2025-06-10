from app.db.core import model
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from app.db.models.types import Teacher
class Role(model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)

    teacher: Mapped[list['Teacher']] = relationship('Teacher', back_populates='role')