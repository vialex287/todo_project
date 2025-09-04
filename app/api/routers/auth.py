from fastapi import APIRouter, Depends, Form, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_async_db
from app.schemas.users import UserAuthSchema, UserCreateSchema, UserResponseSchema
from app.services.auth_service import (
    login_user,
    login_user_token,
    refresh_user_token,
    register_user,
)

router_auth = APIRouter(prefix="/auth", tags=["Auth"])


@router_auth.post("/register", response_model=UserResponseSchema)
async def register(
    user_data: UserCreateSchema, db: AsyncSession = Depends(get_async_db)
):
    return await register_user(user_data, db)


@router_auth.post("/login")
async def login(creds: UserAuthSchema, db: AsyncSession = Depends(get_async_db)):
    return await login_user(creds, db)


@router_auth.post("/token")
async def login_token(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_async_db),
):
    return await login_user_token(response, username, password, db)


@router_auth.post("/refresh")
async def refresh_token(request: Request):
    return await refresh_user_token(request)


@router_auth.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}
