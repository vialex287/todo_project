import pytest
from pydantic import ValidationError

from app.schemas.users import (
    UserAuthSchema,
    UserBaseSchema,
    UserCreateSchema,
    UserResponseSchema,
    UserRoleEnum,
    UserUpdateSchema,
)

# pytest tests/integrations/schemas/test_users_schema.py

# ------------------------------------------------------
# SUCCESS
# ------------------------------------------------------


class TestUserSchemasSuccess:

    def test_user_base_schema_valid(self):
        user = UserBaseSchema(
            name="John", email="john@example.com", role=UserRoleEnum.ADMIN
        )
        assert user.name == "John"
        assert user.email == "john@example.com"
        assert user.role == UserRoleEnum.ADMIN

    def test_user_create_schema_valid(self):
        user = UserCreateSchema(
            name="Alice", email="alice@example.com", password="Secret123"
        )
        assert user.password == "Secret123"

    def test_user_update_schema_partial(self):
        user = UserUpdateSchema(email="new@example.com")
        assert user.email == "new@example.com"
        assert user.name is None
        assert user.role is None

    def test_user_response_schema_valid(self):
        user = UserResponseSchema(
            id=1,
            name="Bob",
            email="bob@example.com",
            role=UserRoleEnum.USER,
            is_active=True,
        )
        assert user.model_dump()["is_active"] is True

    def test_user_auth_schema_valid(self):
        user = UserAuthSchema(email="login@example.com", password="Login123")
        assert user.email == "login@example.com"


# ------------------------------------------------------
# ERRORS
# ------------------------------------------------------


class TestUserSchemasErrors:

    def test_invalid_email_in_base_schema(self):
        with pytest.raises(ValidationError):
            UserBaseSchema(name="Bad", email="not-an-email", role=UserRoleEnum.USER)

    def test_invalid_role_in_base_schema(self):
        with pytest.raises(ValidationError):
            UserBaseSchema(
                name="RoleFail", email="rolefail@example.com", role="INVALID"
            )

    def test_missing_password_in_create_schema(self):
        with pytest.raises(ValidationError):
            UserCreateSchema(name="NoPass", email="nopass@example.com")

    def test_invalid_email_in_update_schema(self):
        with pytest.raises(ValidationError):
            UserUpdateSchema(email="wrong-format")

    def test_missing_required_fields_in_response_schema(self):
        with pytest.raises(ValidationError):
            UserResponseSchema(id=2, email="resp@example.com", is_active=True)

    def test_invalid_email_in_auth_schema(self):
        with pytest.raises(ValidationError):
            UserAuthSchema(email="invalidemail", password="pass123")

    def test_missing_password_in_auth_schema(self):
        with pytest.raises(ValidationError):
            UserAuthSchema(email="auth@example.com")
