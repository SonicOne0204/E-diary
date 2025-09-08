import asyncio
import pytest, pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings
from app.db.models.schools import School
from app.db.core import Base, get_async_db
from app.main import app

test_engine = create_async_engine(settings.TEST_DB_URL, echo=True, future=True)
TestSessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession ,autoflush=False, autocommit=False)


@pytest_asyncio.fixture(scope='function')
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def get_test_db(setup_db):
    async with TestSessionLocal() as db:
        yield db 

@pytest_asyncio.fixture()
async def create_school(get_test_db):
    db = get_test_db
    school = School(
        name="School", short_name="SH", country="China", address="ShiaChan street 32"
    )
    db.add(school)
    await db.commit() 
    await db.refresh(school)  
    
    yield school
    


async def override_get_db():
    async with TestSessionLocal() as db:
        yield db


app.dependency_overrides[get_async_db] = override_get_db
