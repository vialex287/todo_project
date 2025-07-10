from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import engine

async def get_async_db():
    async with AsyncSession(engine) as session:
        yield session


# проверка на существование пользователя
async def user_valid(user, db: AsyncSession = Depends(get_async_db)):
    if not user:
        raise HTTPException(status_code=404, detail="User is not found")
    return True

# проверка на существование задания
async def task_valid(task, db: AsyncSession = Depends(get_async_db)):
    if not task:
        raise HTTPException(status_code=404, detail="Task is not found")
    return True