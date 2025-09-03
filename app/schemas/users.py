from enum import Enum as PyEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.dependencies import validate_email


class UserRoleEnum(str, PyEnum):
    ADMIN = "admin"
    USER = "user"


class UserBaseSchema(BaseModel):
    name: str
    email: str
    role: UserRoleEnum = Field(default=UserRoleEnum.USER)

    @field_validator("email")
    @classmethod
    def check_email(cls, email_):
        return validate_email(email_)


class UserCreateSchema(UserBaseSchema):
    password: str


class UserUpdateSchema(BaseModel):
    name: str | None = Field(default=None)
    email: str | None = Field(default=None, json_schema_extra={"unique": True})
    password: str | None = Field(default=None)
    role: UserRoleEnum | None = Field(default=None)

    @field_validator("email")
    @classmethod
    def check_email(cls, email_):
        return validate_email(email_)


class UserResponseSchema(UserBaseSchema):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserAuthSchema(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def check_email(cls, email_):
        return validate_email(email_)
