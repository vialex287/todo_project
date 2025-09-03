import pytest

from app.models.users import User
from app.schemas.users import UserRoleEnum

# pytest tests\units\models\test_user_models.py -v


class TestUserModelValid:

    # default #
    def test_user_create_default(self):
        user = User(name="Test User", email="test@example.com", password="password_123")

        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.password == "password_123"
        assert user.role in [None, UserRoleEnum.USER]
        assert user.is_active in [None, True]
        assert user.tasks == []

    def test_user_columns_exist(self):
        assert hasattr(User, "id")
        assert hasattr(User, "name")
        assert hasattr(User, "email")
        assert hasattr(User, "password")
        assert hasattr(User, "role")
        assert hasattr(User, "is_active")

    # email #
    def test_user_email_unique_constraint(self):
        assert User.email.unique is True

    # role #
    def test_user_role_default(self):
        assert User.role.default.arg == UserRoleEnum.USER

    def test_user_with_custom_role(self):
        user = User(
            name="Admin User",
            email="admin@example.com",
            password="hashed_password_123",
            role=UserRoleEnum.ADMIN,
        )

        assert user.role == UserRoleEnum.ADMIN

    def test_user_role_not_nullable(self):
        assert User.role.nullable is False

    # password #
    def test_user_password_not_nullable(self):
        assert User.password.nullable is False

    # relationship tasks
    def test_user_relationship_tasks(self):
        assert hasattr(User, "tasks")
        assert User.tasks.property.uselist is True
