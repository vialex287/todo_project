from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import re

from app.core.database import engine

async def get_async_db():
    async with AsyncSession(engine) as session:
        yield session


# проверка на существование пользователя
async def user_valid(user):
    if not user:
        raise HTTPException(status_code=404, detail="User is not found")
    return True

# проверка на существование задания
async def task_valid(task):
    if not task:
        raise HTTPException(status_code=404, detail="Task is not found")
    return True


def validate_email(email: str | None) -> str | None:
    if email is None:
        return None

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_regex, email):
        raise ValueError('Invalid email format')
    return email