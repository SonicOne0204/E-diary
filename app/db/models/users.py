from sqlalchemy import String, Integer, Sequence, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.db.core import model 

class User(model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)
    

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'admin' 
    }



