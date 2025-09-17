from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.auth import get_current_user
from app.dependencies import get_async_db
from app.models.users import User
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
    user_id: int,
    task_data: TaskCreateSchema,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await create_task_user(
        user_id=user_id, task_data=task_data, db=db, current_user=current_user
    )


@router_tasks.get("/", response_model=List[TaskResponseSchema])
async def get_tasks(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await get_tasks_from_user(user_id=user_id, db=db, current_user=current_user)


@router_tasks.get("/{task_id}", response_model=TaskResponseSchema)
async def get_task(
    user_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await get_task_from_user(
        user_id=user_id, task_id=task_id, db=db, current_user=current_user
    )


@router_tasks.put("/{task_id}", response_model=TaskResponseSchema)
async def update_task(
    user_id: int,
    task_id: int,
    new_data: TaskUpdateSchema,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await update_task_from_user(
        user_id=user_id,
        task_id=task_id,
        new_data=new_data,
        db=db,
        current_user=current_user,
    )


@router_tasks.delete("/{task_id}")
async def delete_task(
    user_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await delete_task_from_user(
        user_id=user_id, task_id=task_id, db=db, current_user=current_user
    )
