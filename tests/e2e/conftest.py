import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.dependencies import get_async_db
from main import app


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


# --- DATABASE --- #

DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine_test = create_async_engine(DATABASE_URL, future=True)
AsyncSessionLocal = sessionmaker(
    engine_test, expire_on_commit=False, class_=AsyncSession
)


async def override_get_async_db():
    async with AsyncSessionLocal() as session:
        yield session


app.dependency_overrides[get_async_db] = override_get_async_db


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


# --- AUTH --- #


@pytest.fixture
async def registered_user(client):

    response = await client.post(
        "/auth/register",
        json={
            "name": "Alice",
            "email": email_random(),
            "password": "secret123",
            "role": "user",
        },
    )

    assert response.status_code == 200
    data = response.json()

    return {
        "id": data["id"],
        "email": data["email"],
        "role": data["role"],
        "name": data["name"],
    }


@pytest.fixture
async def registered_admin(client):

    response = await client.post(
        "/auth/register",
        json={
            "name": "Admin",
            "email": email_random(),
            "password": "admin123",
            "role": "admin",
        },
    )

    assert response.status_code == 200
    data = response.json()

    return {
        "id": data["id"],
        "email": data["email"],
        "role": data["role"],
        "name": data["name"],
    }


@pytest.fixture
async def user_token(client, registered_user):
    resp = await client.post(
        "/auth/login", json={"email": registered_user["email"], "password": "secret123"}
    )
    return resp.json()["access_token"]


@pytest.fixture
async def admin_token(client, registered_admin):
    resp = await client.post(
        "/auth/login", json={"email": registered_admin["email"], "password": "admin123"}
    )
    return resp.json()["access_token"]
