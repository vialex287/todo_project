from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional


class TaskEnum(str, PyEnum):
    DONE = "Done"
    IN_PROGRESS = "In progress"
    EXPIRED = "Expired"


class TaskBaseSchema(BaseModel):
    title: str
    description: str
    status: TaskEnum = Field(default=TaskEnum.IN_PROGRESS)
    deadline: datetime
    is_completed: bool = Field(default=False)


class TaskCreateSchema(TaskBaseSchema):
    pass


class TaskUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskEnum] = None
    deadline: Optional[datetime] = None
    is_completed: Optional[bool] = None


class TaskResponseSchema(TaskBaseSchema):
    id: int
    user_id: int

    class Config:
        from_attributes = True