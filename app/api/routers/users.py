from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_async_db, user_valid
from app.schemas.users import UserCreateSchema, UserUpdateSchema, UserResponseSchema
from app.models import User, Task
from typing import List

router_users = APIRouter(
    prefix="/users",
    tags=["User"]
)


# создать пользователя
@router_users.post("/", response_model=UserResponseSchema)
async def create_user(
        user_data: UserCreateSchema,
        db: AsyncSession = Depends(get_async_db)
    ):
    new_user = User(
        name=user_data.name,
        email=user_data.email
    )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred when creating the object"
        )


# показать всех пользователей
@router_users.get("/", response_model=List[UserResponseSchema])
async def get_users(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()

    if not users:
        return JSONResponse(
            status_code=200,
            content={"message": "User list is empty"}
        )
    return users


# показать конкретного пользователя
@router_users.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(user_id: int,
                   db: AsyncSession = Depends(get_async_db)):
    user = await db.get(User, user_id)
    await user_valid(user)

    try:
        return user
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred when getting the object"
        )


@router_users.put("/{user_id}")
async def update_user(
        user_id: int,
        new_data: UserUpdateSchema,
        db: AsyncSession = Depends(get_async_db)
):
    user = await db.get(User, user_id)
    await user_valid(user)

    if new_data.name:
        user.name = new_data.name

    if new_data.email is not None:
        user.email = new_data.email
    try:
        await db.commit()
        await db.refresh(user)
        return user
    except:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred when updating the object")


@router_users.delete("/{user_id}")
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_async_db)
):
    user = await db.get(User, user_id)
    await user_valid(user)

    try:
        await db.delete(user)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred when deleting an object"
        )