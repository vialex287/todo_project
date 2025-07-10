from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum as PyEnum

class TaskEnum(str, PyEnum):
    DONE = "Done"
    IN_PROGRESS = "In progress"
    EXPIRED = "Expired"


class TaskCreateSchema(BaseModel):
    title: str
    description: str
    status: TaskEnum = Field(default=TaskEnum.IN_PROGRESS)
    deadline: datetime
    is_complited: bool = Field(default=False)

class TaskUpdateSchema(BaseModel):
    title: str | None
    description: str | None
    deadline: datetime | None
    is_complited: bool | None = Field(default=False)


class TaskResponseSchema(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    status: TaskEnum
    deadline: datetime
    is_complited: bool

    class Config:
        from_attributes = True