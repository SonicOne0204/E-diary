from sqlalchemy import String, Integer, Sequence, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List, TYPE_CHECKING
from db.core import model
from .roles import Role

class User(model):
    __tablename__ = 'users'
 
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'))
    
    role: Mapped['Role'] = relationship('Role', back_populates='users')
