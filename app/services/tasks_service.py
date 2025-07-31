from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_async_db, user_valid, task_valid
from app.schemas.tasks import TaskCreateSchema, TaskUpdateSchema
from app.models import Task, User

async def create_task_user(
        user_id: int,
        task_data: TaskCreateSchema,
        db: AsyncSession = Depends(get_async_db)
    ):
    user = await db.get(User, user_id)
    await user_valid(user)

    new_task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status.value,
        deadline=task_data.deadline,
        is_complited=False
    )

    try:
        await new_task.update_status()
        db.add(new_task)
        await db.commit()
        await db.refresh(new_task)
        return new_task
    except:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred when creating the object"
        )


async def get_tasks_from_user(
        user_id: int,
        db: AsyncSession = Depends(get_async_db)
):
    user = await db.get(User, user_id)
    await user_valid(user)

    res_tasks = await db.execute(select(Task).where(Task.user == user))
    tasks = res_tasks.scalars().all()

    if not tasks:
        return JSONResponse(
            status_code=200,
            content={"message": "User list is empty"}
        )
    return tasks


async def get_task_from_user(user_id: int,
                   task_id: int,
                   db: AsyncSession = Depends(get_async_db)):

    user = await db.get(User, user_id)
    await user_valid(user)

    task = await db.get(Task, task_id)
    await task_valid(task)

    try:
        return task
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Произошла внутренняя ошибка сервера"
        )


async def update_task_from_user(
        user_id: int,
        task_id: int,
        new_data: TaskUpdateSchema,
        db: AsyncSession = Depends(get_async_db)
):
    user = await db.get(User, user_id)
    await user_valid(user)

    task = await db.get(Task, task_id)
    await task_valid(task)

    if new_data.title:
        task.title = new_data.title

    if new_data.description:
        task.description = new_data.description

    if new_data.deadline:
        task.deadline = new_data.deadline

    if new_data.is_complited:
        task.is_complited = new_data.is_complited

    try:
        await task.update_status()
        await db.commit()
        await db.refresh(task)
        return task
    except:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred when updating the object"
        )


async def delete_task_from_user(
        user_id: int,
        task_id: int,
        db: AsyncSession = Depends(get_async_db)
):
    user = await db.get(User, user_id)
    await user_valid(user)

    task = await db.get(Task, task_id)
    await task_valid(task)

    try:
        await db.delete(task)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except:
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred when deleting the object"
        )