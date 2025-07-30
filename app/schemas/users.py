from pydantic import BaseModel, Field
from enum import Enum as PyEnum

class UserRoleEnum(str, PyEnum):
    ADMIN = "admin"
    USER = "user"


class UserCreateSchema(BaseModel):
    user_id: int
    name: str
    email: str = Field(unique=True)
    hashed_password: str
    role: UserRoleEnum = Field(default=UserRoleEnum.USER)


class UserUpdateSchema(BaseModel):
    name: str | None = None
    email: str | None = Field(unique=True)
    hashed_password: str


class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: str
    hashed_password: str
    role: UserRoleEnum
    is_active: bool

    class Config:
        from_attributes = True

class UserAuthSchema(BaseModel):
    email: str
    hashed_password: str