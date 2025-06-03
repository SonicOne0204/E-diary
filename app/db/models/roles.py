from sqlalchemy import String, Integer, Sequence, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List, TYPE_CHECKING
from database.core import model

class Role(model):
    __tablename__ = 'roles'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    users: Mapped[List["User"]] = relationship('User', back_populates= 'role')


