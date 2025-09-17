from datetime import datetime, timedelta, timezone

import pytest

from app.models.tasks import Task
from app.models.users import User
from app.schemas.tasks import TaskEnum


class TestTaskModel:
    def test_task_creation_basic(self):
        task = Task(title="Test Task", description="Test description", user_id=1)

        assert task.title == "Test Task"
        assert task.description == "Test description"
        assert task.user_id == 1
        assert task.status in [None, TaskEnum.IN_PROGRESS]
        assert task.is_completed in [None, False]

    def test_task_columns_exist(self):
        assert hasattr(Task, "id")
        assert hasattr(Task, "title")
        assert hasattr(Task, "description")
        assert hasattr(Task, "status")
        assert hasattr(Task, "deadline")
        assert hasattr(Task, "is_completed")
        assert hasattr(Task, "user_id")

    def test_task_relationships_exist(self):
        user = User(name="Test", email="test@test.com", password="123")
        task = Task(title="Task", user=user)
        assert task.user is user
        assert user.tasks[0] is task

    def test_task_foreign_key(self):
        fk = list(Task.user_id.foreign_keys)[0]
        assert fk.target_fullname == "Users.id"

    def test_task_repr(self):
        task = Task(id=1, title="Hello")
        assert "Task" in repr(task)
        assert "Hello" in repr(task)


@pytest.mark.asyncio
class TestTaskUpdateStatus:

    async def test_task_update_status_done(self):
        task = Task(is_completed=True)
        await task.update_status()
        assert task.status == TaskEnum.DONE

    async def test_task_update_status_expired(self):
        task = Task(
            is_completed=False, deadline=datetime.now(timezone.utc) - timedelta(days=1)
        )
        await task.update_status()
        assert task.status == TaskEnum.EXPIRED

    async def test_task_update_status_in_progress(self):
        task = Task(
            is_completed=False, deadline=datetime.now(timezone.utc) + timedelta(days=1)
        )
        await task.update_status()
        assert task.status == TaskEnum.IN_PROGRESS
