import asyncio
import re
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import engine


async def get_async_db():
    async with AsyncSession(engine) as session:
        yield session


async def user_valid(user):
    if not user:
        raise HTTPException(status_code=404, detail="User is not found")
    return True


async def task_valid(task):
    if not task:
        raise HTTPException(status_code=404, detail="Task is not found")
    return True


def validate_email(email: str | None) -> str | None:
    if email is None:
        return None

    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(email_regex, email):
        raise ValueError("Invalid email format")
    return email

  
async def wait_for_db():
    import aiomysql

    for _ in range(5):
        try:
            conn = await aiomysql.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                db=settings.DB_NAME,
            )
            conn.close()
            print("✅ DB is ready!")
            return
        except Exception as e:
            print("⏳ Waiting for DB...", e)
            await asyncio.sleep(1)
    raise Exception("❌ Could not connect to DB")
