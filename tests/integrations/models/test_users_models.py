import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError, StatementError

from app.models.users import User
from app.models.tasks import Task
from app.schemas.users import UserRoleEnum

# pytest tests/integrations/models/test_users_models.py

# ------------------------------------------------------
# SUCCESS
# ------------------------------------------------------

class TestUserModelSuccess:

    @pytest.mark.asyncio
    async def test_create_user(self, test_db):
        user = User(
            name="Alice",
            email="alice@example.com",
            password="hashed_pw",
            role=UserRoleEnum.ADMIN,
            is_active=True
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        assert user.id is not None
        assert user.name == "Alice"
        assert user.email == "alice@example.com"
        assert user.role == UserRoleEnum.ADMIN
        assert user.is_active is True


    @pytest.mark.asyncio
    async def test_update_user(self, test_db, user_factory):
        user = user_factory(email="bob@example.com", name="Bob")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        user.name = "Bobby"
        await test_db.commit()
        await test_db.refresh(user)

        assert user.name == "Bobby"

    @pytest.mark.asyncio
    async def test_delete_user(self, test_db, user_factory):
        user = user_factory(email="delete@example.com")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        user_id = user.id
        await test_db.delete(user)
        await test_db.commit()

        deleted = await test_db.get(User, user_id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_user_with_tasks_relationship(self, test_db, user_factory):
        user = user_factory(email="withtasks@example.com")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        # создаем связанные задачи
        task1 = Task(title="Task 1", description="desc1", user_id=user.id)
        task2 = Task(title="Task 2", description="desc2", user_id=user.id)
        test_db.add_all([task1, task2])
        await test_db.commit()

        result = await test_db.execute(
            select(User).options(selectinload(User.tasks)).where(User.id == user.id)
        )
        user_with_tasks = result.scalar_one()

        assert len(user_with_tasks.tasks) == 2
        titles = {t.title for t in user_with_tasks.tasks}
        assert "Task 1" in titles
        assert "Task 2" in titles


# ------------------------------------------------------
# ERRORS
# ------------------------------------------------------

class TestUserModelErrors:

    @pytest.mark.asyncio
    async def test_unique_email_constraint(self, test_db, user_factory):
        user1 = user_factory(email="unique@example.com")
        user2 = user_factory(email="unique@example.com")

        test_db.add(user1)
        await test_db.commit()

        test_db.add(user2)
        with pytest.raises(IntegrityError):
            await test_db.commit()
        await test_db.rollback()

    @pytest.mark.asyncio
    async def test_null_password_not_allowed(self, test_db):
        user = User(
            name="NoPass",
            email="nopass@example.com",
            password=None
        )
        test_db.add(user)

        with pytest.raises(IntegrityError):
            await test_db.commit()
        await test_db.rollback()

    def test_invalid_enum_python(self):
        with pytest.raises(ValueError):
            UserRoleEnum("INVALID")