from pydantic import BaseModel, Field


class UserCreateSchema(BaseModel):
    task_id: int
    name: str
    email: str = Field(unique=True)

class UserUpdateSchema(BaseModel):
    name: str | None = None
    email: str | None = Field(unique=True)

class UserResponseSchema(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True