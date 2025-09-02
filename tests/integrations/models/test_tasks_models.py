import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm.exc import StaleDataError

from app.models.tasks import Task
from app.models.users import User
from app.schemas.tasks import TaskEnum

# pytest tests/integrations/models/test_tasks_models.py

# ------------------------------------------------------
# SUCCESS
# ------------------------------------------------------

class TestTaskModelSuccess:

    @pytest.mark.asyncio
    async def test_create_task_minimal(self, test_db):
        task = Task(title="Test Task", description="Simple description")
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.status == TaskEnum.IN_PROGRESS
        assert isinstance(task.deadline, datetime)

    @pytest.mark.asyncio
    async def test_task_with_user_relationship(self, test_db):
        user = User(name="TaskOwner", email="owner@example.com", password="pw")
        task = Task(title="With User", user=user)

        test_db.add_all([user, task])
        await test_db.commit()
        await test_db.refresh(task)

        assert task.user_id == user.id
        assert task.user.email == "owner@example.com"

    @pytest.mark.asyncio
    async def test_update_status_to_done(self, test_db):
        task = Task(title="Completed Task", is_completed=True)
        await task.update_status()
        assert task.status == TaskEnum.DONE

    @pytest.mark.asyncio
    async def test_update_status_to_expired(self):
        expired_deadline = datetime.now(timezone.utc) - timedelta(days=1)
        task = Task(title="Expired Task", deadline=expired_deadline)
        await task.update_status()
        assert task.status == TaskEnum.EXPIRED

    @pytest.mark.asyncio
    async def test_update_status_in_progress(self, test_db):
        future_deadline = datetime.now(timezone.utc) + timedelta(days=1)
        task = Task(title="In Progress Task", deadline=future_deadline.replace(tzinfo=timezone.utc))
        test_db.add(task)
        await test_db.flush()

        await task.update_status()
        assert task.status == TaskEnum.IN_PROGRESS

# ------------------------------------------------------
# ERRORS
# ------------------------------------------------------

class TestTaskModelErrors:

    def test_invalid_status_enum_value(self):
        with pytest.raises(ValueError):
            TaskEnum("INVALID")

    @pytest.mark.asyncio
    async def test_missing_required_field(self, test_db):
        task = Task()
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)
        assert task.title is None
        assert task.description is None

    @pytest.mark.asyncio
    async def test_relationship_invalid_user(self, test_db):
        task = Task(title="Orphan Task", user_id=9999)
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)

        assert task.user_id == 9999

    def test_repr_method(self):
        task = Task(id=1, title="Repr Task", status=TaskEnum.IN_PROGRESS)
        repr_str = repr(task)
        assert "Task id=1" in repr_str
        assert "Repr Task" in repr_str
        assert "IN_PROGRESS" in repr_str
