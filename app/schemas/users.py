from pydantic import BaseModel, Field

class UserCreateSchema(BaseModel):
    task_id: int
    name: str
    email: str = Field(unique=True)
    hashed_password: str


class UserUpdateSchema(BaseModel):
    name: str | None = None
    email: str | None = Field(unique=True)
    hashed_password: str


class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: str
    hashed_password: str
    is_active: bool

    class Config:
        from_attributes = True

class UserAuthSchema(BaseModel):
    email: str
    hashed_password: str