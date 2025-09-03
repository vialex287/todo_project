from datetime import datetime, timedelta, timezone

import pytest

from app.models import Task
from app.schemas.tasks import TaskEnum


@pytest.fixture
def task_factory():
    def _create_task(
        user_id: int,
        title: str = "Default task",
        description: str = "Some description",
        status: TaskEnum = TaskEnum.IN_PROGRESS,
        deadline: datetime = None,
        is_completed: bool = False,
    ):
        return Task(
            user_id=user_id,
            title=title,
            description=description,
            status=status,
            deadline=deadline or (datetime.now(timezone.utc) + timedelta(days=1)),
            is_completed=is_completed,
        )

    return _create_task
