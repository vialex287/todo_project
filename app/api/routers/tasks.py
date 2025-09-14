from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_async_db
from app.schemas.tasks import TaskCreateSchema, TaskResponseSchema, TaskUpdateSchema
from app.services.tasks_service import (
    create_task_user,
    delete_task_from_user,
    get_task_from_user,
    get_tasks_from_user,
    update_task_from_user,
)

router_tasks = APIRouter(prefix="/{user_id}/tasks", tags=["Tasks"])


@router_tasks.post("/", response_model=TaskResponseSchema)
async def create_task(
    user_id: int, task_data: TaskCreateSchema, db: AsyncSession = Depends(get_async_db)
):
    return await create_task_user(user_id, task_data, db)


@router_tasks.get("/", response_model=List[TaskResponseSchema])
async def get_tasks(user_id: int, db: AsyncSession = Depends(get_async_db)):
    return await get_tasks_from_user(user_id, db)


@router_tasks.get("/{task_id}", response_model=TaskResponseSchema)
async def get_task(
    user_id: int, task_id: int, db: AsyncSession = Depends(get_async_db)
):
    return await get_task_from_user(user_id, task_id, db)


@router_tasks.put("/{task_id}", response_model=TaskResponseSchema)
async def update_task(
    user_id: int,
    task_id: int,
    new_data: TaskUpdateSchema,
    db: AsyncSession = Depends(get_async_db),
):
    return await update_task_from_user(user_id, task_id, new_data, db)


@router_tasks.delete("/{task_id}")
async def delete_task(
    user_id: int, task_id: int, db: AsyncSession = Depends(get_async_db)
):
    return await delete_task_from_user(user_id, task_id, db)
