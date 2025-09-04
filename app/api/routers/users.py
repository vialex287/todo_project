from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.auth import get_current_user
from app.dependencies import get_async_db
from app.models.users import User
from app.schemas.users import UserResponseSchema, UserUpdateSchema
from app.services.users_service import delete_user_, get_user_, get_users_, update_user_

router_users = APIRouter(prefix="/users", tags=["User"])


@router_users.get("/", response_model=List[UserResponseSchema])
async def get_users(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await get_users_(db, current_user)


@router_users.get("/{user_id}", response_model=UserResponseSchema)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await get_user_(user_id, db, current_user)


@router_users.put("/{user_id}")
async def update_user(
    user_id: int,
    new_data: UserUpdateSchema,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await update_user_(user_id, new_data, db, current_user)


@router_users.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await delete_user_(user_id, db, current_user)
