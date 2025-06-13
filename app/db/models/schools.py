from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Boolean

from app.db.core import model

class School(model):
    __tablename__ = 'schools'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    short_name: Mapped[str] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    adress: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    principals: Mapped[list['Principal']] = relationship('Principal', back_populates='school')
    teachers: Mapped[list['Teacher']] = relationship('Teacher', back_populates='school')
    students: Mapped[list['Student']] = relationship('Student', back_populates='school')
    groups: Mapped[list['Group']] = relationship('Group', back_populates='school_group')