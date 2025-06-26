from app.db.core import model
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, Boolean

class Role(model):
    __tablename__ = 'roles'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=True)

    teachers: Mapped[list['Teacher']] = relationship('Teacher', back_populates='role', passive_deletes=True)