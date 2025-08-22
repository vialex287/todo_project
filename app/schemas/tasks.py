from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum as PyEnum

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
    title: str | None = Field(default=None)
    description: str | None  = Field(default=None)
    status: TaskEnum | None  = Field(default=None)
    deadline: datetime | None  = Field(default=None)


class TaskResponseSchema(TaskBaseSchema):
    id: int
    user_id: int

    class Config:
        from_attributes = True