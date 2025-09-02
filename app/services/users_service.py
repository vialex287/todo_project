from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_async_db, user_valid
from app.schemas.users import UserUpdateSchema
from app.models import User
from app.api.auth.auth import get_current_user


# показать всех пользователей
async def get_users_(
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not admin")

    result = await db.execute(select(User))
    users = result.scalars().all()

    if not users:
        return JSONResponse(
            status_code=200,
            content={"message": "User list is empty"}
        )
    return users


# показать конкретного пользователя
async def get_user_(user_id: int,
                   db: AsyncSession = Depends(get_async_db),
                   current_user: User = Depends(get_current_user)
):
    user = await db.get(User, user_id)
    await user_valid(user)

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not admin")

    try:
        return user
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred when getting the object"
        )


async def update_user_(
        user_id: int,
        new_data: UserUpdateSchema,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    user = await db.get(User, user_id)
    await user_valid(user)


    if current_user.id != user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not admin")

    if new_data.name:
        user.name = new_data.name

    if new_data.email is not None:
        user.email = new_data.email

    if new_data.password:
        user.password = new_data.password

    if current_user.role != "admin" and new_data.role is not None:
        raise HTTPException(status_code=403, detail="You are not admin")
    elif current_user.role == "admin" and new_data.role is not None:
        user.role = new_data.role

    try:
        await db.commit()
        await db.refresh(user)
        return user
    except:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred when updating the object")


async def delete_user_(
        user_id: int,
        db: AsyncSession = Depends(get_async_db),
        current_user: User = Depends(get_current_user)
):
    user = await db.get(User, user_id)
    await user_valid(user)

    if current_user.role != "admin" and current_user.id != user.id:
        raise HTTPException(status_code=403, detail="You are not admin")

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