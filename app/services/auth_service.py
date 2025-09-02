from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import APIRouter, Depends, HTTPException, Form, Response, Request
from app.models import User
from app.schemas.users import UserCreateSchema, UserAuthSchema
from app.api.auth.auth import verify_password, hash_password, create_access_token, create_refresh_token, verify_refresh_token
from app.dependencies import get_async_db


async def register_user(user_data: UserCreateSchema,
                        db: AsyncSession = Depends(get_async_db)) -> User:

    hashed = hash_password(user_data.password)

    user = await db.execute(select(User).where(User.email == user_data.email))
    if user.scalars().first():
        raise HTTPException(status_code=409, detail="Email already exist")

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed,
        is_active=True,
        role=user_data.role
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


async def login_user(creds: UserAuthSchema,
                     db: AsyncSession = Depends(get_async_db)):

    res = await db.execute(select(User).where(User.email == creds.email))
    user = res.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="User is not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is blocked")

    if not verify_password(creds.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})


    return {
            "email": user.email,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }


async def login_user_token(response: Response,
                           username: str = Form(...),
                           password: str = Form(...),
                           db: AsyncSession = Depends(get_async_db)):
    res = await db.execute(select(User).where(User.email == username))
    user = res.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="User is not found")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="User is blocked")

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    # tokens
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    # cookies
    response.set_cookie("access_token", access_token, httponly=True, max_age=900)
    response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=86400)

    return {
        "email": user.email,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


async def refresh_user_token(request: Request):
    try:
        payload = verify_refresh_token(request)
        email: str = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": email})
    return {
        "message": "Refresh token is valid",
        "email": email,
        "access_token": new_access_token,
        "token_type": "bearer",
    }

