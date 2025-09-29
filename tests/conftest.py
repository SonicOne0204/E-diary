import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from app.db.core import Base, get_async_db
from app.main import app
from app.db.models.users import User
from app.services.auth import get_current_user

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DB_URL, future=True)
TestingSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def override_get_current_user():
    return User(
        username="admin",
        hashed_password="eyJhbGciOiJIUzI1NiJ9.YWRtaW4.J1moEvk4tebh7ihwQWK5RIMQNw26JY-Pv2OEpNK4nG8",
        first_name="admin",
        last_name="admin",
        email="admin@gmail.com",
    )


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture(scope="function", autouse=True)
def setup_dependency_overrides():
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_async_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def test_user(db_session):
    user = User(
        username="testuser",
        hashed_password="hashed_password_here",
        first_name="Test",
        last_name="User",
        email="test@example.com",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
