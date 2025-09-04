import pytest
from pydantic import ValidationError

from app.schemas.users import (
    UserAuthSchema,
    UserCreateSchema,
    UserResponseSchema,
    UserRoleEnum,
    UserUpdateSchema,
)

# pytest tests\units\schemas\test_user_schema.py -v


class TestUserCreateSchema:

    def test_valid(self):
        """A test with correct data"""

        data = {
            "name": "Anna",
            "email": "anna@example.com",
            "password": "Anna123",
        }

        schema = UserCreateSchema(**data)
        assert schema.name == "Anna"
        assert schema.email == "anna@example.com"
        assert schema.password == "Anna123"
        assert schema.role == UserRoleEnum.USER

    def test_default_role(self):
        """A test with a default role"""

        data = {
            "name": "Alice",
            "email": "alice@example.com",
            "password": "hashedpass123",
        }

        schema = UserCreateSchema(**data)
        assert schema.role == UserRoleEnum.USER

    def test_custom_role(self):
        """A test with a custom role"""

        data = {
            "name": "Bob",
            "email": "bob@example.com",
            "password": "secure123",
            "role": UserRoleEnum.ADMIN,
        }

        schema = UserCreateSchema(**data)
        assert schema.role == UserRoleEnum.ADMIN

    def test_field_ignored(self):
        """a test to check if a non-existent field is ignored"""

        data = {
            "name": "Bob",
            "email": "bob@example.com",
            "password": "secure123",
            "id": 999,
            "field": "value",
        }
        schema = UserCreateSchema(**data)
        assert not hasattr(schema, "id")
        assert not hasattr(schema, "field")

    # errors #

    def test_invalid_email(self):
        data = {
            "name": "Alice",
            "email": "not-an-email",
            "password": "123",
        }

        with pytest.raises(ValidationError):
            UserCreateSchema(**data)

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            UserCreateSchema(name="Alice")


class TestUserUpdateSchema:
    def test_empty_update(self):
        schema = UserUpdateSchema()
        assert schema.name is None
        assert schema.email is None
        assert schema.password is None
        assert schema.role is None

    def test_update_name(self):
        schema = UserUpdateSchema(name="NewName")
        assert schema.name == "NewName"

    def test_update_password(self):
        schema = UserUpdateSchema(password="Fcg43gv")
        assert schema.password == "Fcg43gv"

    def test_update_role(self):
        schema = UserUpdateSchema(role=UserRoleEnum.ADMIN)
        assert schema.role == UserRoleEnum.ADMIN

    def test_valid_email(self):
        schema = UserUpdateSchema(email="test@example.com")
        assert schema.email == "test@example.com"

    # errors #

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserUpdateSchema(email="not-an-email")  # ✅


class TestUserResponseSchema:

    def test_from_attributes(self):
        class MockUser:
            def __init__(self):
                self.id = 1
                self.name = "Test"
                self.email = "test@example.com"
                self.role = UserRoleEnum.USER
                self.is_active = True

        mock_user = MockUser()

        schema = UserResponseSchema.model_validate(mock_user)
        assert schema.id == 1
        assert schema.name == "Test"
        assert schema.email == "test@example.com"

    def test_basic(self):
        data = {
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
            "role": UserRoleEnum.USER,
            "is_active": True,
        }

        schema = UserResponseSchema(**data)
        assert schema.id == 1
        assert schema.name == "Anna"
        assert schema.email == "anna@example.com"
        assert schema.role == UserRoleEnum.USER
        assert schema.is_active is True

    # errors #

    def test_missing_required_field(self):
        data = {
            "id": 1,
            "name": "Anna",
            "email": "anna@example.com",
        }

        with pytest.raises(ValidationError):
            UserResponseSchema(**data)

    def test_user_response_invalid_email(self):
        data = {"id": 1, "name": "Anna", "email": "invalid-email", "is_active": True}
        with pytest.raises(ValidationError):
            UserResponseSchema(**data)


class TestUserAuthSchema:

    def test_valid(self):
        data = {
            "email": "user@example.com",
            "password": "Password123",
        }

        schema = UserAuthSchema(**data)
        assert schema.email == "user@example.com"
        assert schema.password == "Password123"

    # errors #

    def test_invalid_email(self):
        data = {
            "email": "no email",
            "password": "Password123",
        }

        with pytest.raises(ValidationError):
            UserAuthSchema(**data)

    def test_missing_email(self):
        with pytest.raises(ValidationError):
            UserAuthSchema(password="Password123")

    def test_missing_password(self):
        with pytest.raises(ValidationError):
            UserAuthSchema(email="user@example.com")
