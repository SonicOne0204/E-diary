from sqlalchemy import select

from app.db.core import AsyncSessionLocal
from app.db.models.users import User
from app.schemas.users import UserTypes
from app.core.security import hash_password


async def create_admin():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.type == UserTypes.admin))
        admin = result.scalars().first()
        if admin:
            print("Admin user already exists.")
            print(f'admin id = {admin.id}, admin name = {admin.username}')
            return
        username = input("Enter username:")
        email = input("Enter email:")
        password = input("Enter password:")
        new_admin = User(
            username=username,
            email=email,
            type=UserTypes.admin,
            hashed_password=hash_password(password),
        )
        db.add(new_admin)
        await db.commit()
        print("Admin user created.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(create_admin())
