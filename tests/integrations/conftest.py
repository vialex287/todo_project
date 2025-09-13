# tests/integrations/api/conftest.py

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.api.auth.auth import get_current_user
from app.core.database import Base
from app.models.users import User
from main import app

DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def email_random():
    from random import shuffle

    name_email = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
    ]
    shuffle(name_email)
    return f'{"".join(name_email[:8])}@example.com'


# ---------------------------
# USER FACTORY
# ---------------------------


@pytest.fixture
def user_factory():
    def _make_user(
        email: str | None = None,
        name: str = "tester",
        password: str = "Test123",
        role: str = "admin",
        is_active: bool = True,
    ):
        return User(
            email=email or email_random(),
            name=name,
            password=password,
            role=role,
            is_active=is_active,
        )

    return _make_user


# ---------------------------
# DATABASE FIXTURES
# ---------------------------


@pytest.fixture(scope="session")
def async_engine():
    return create_async_engine(DATABASE_URL, echo=True)


@pytest.fixture(scope="session", autouse=True)
async def create_tables(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def test_db(async_engine):
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest.fixture(autouse=True)
async def clean_db(test_db):
    yield
    for table in reversed(Base.metadata.sorted_tables):
        await test_db.execute(table.delete())
    await test_db.commit()


# ---------------------------
# CLIENT FIXTURE
# ---------------------------


@pytest.fixture
async def test_client(test_db, user_factory):

    from app.dependencies import get_async_db

    async def override_get_db():
        yield test_db

    _current_user = {"user": None}

    async def override_get_current_user():
        return _current_user["user"]

    app.dependency_overrides[get_async_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        client.set_current_user = lambda u: _current_user.update({"user": u})
        yield client

    app.dependency_overrides.clear()
