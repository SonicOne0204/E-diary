from app.db.core import SessionLocal
from app.db.models.users import User
from app.schemas.users import UserTypes
from app.core.security import hash_password

def create_admin():
    db = SessionLocal()
    admin = db.query(User).filter_by(type=UserTypes.admin).first()
    if admin:
        print("Admin user already exists.")
        return
    username = input('Enter username:')
    email = input('Enter email:')
    password = input('Enter password:')
    new_admin = User(
        username=username,
        email=email,
        type=UserTypes.admin,
        hashed_password=hash_password(password)
    )
    db.add(new_admin)
    db.commit()
    print("Admin user created.")

if __name__ == "__main__":
    create_admin()