from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.schemas.tasks import (
    TaskBaseSchema,
    TaskCreateSchema,
    TaskEnum,
    TaskResponseSchema,
    TaskUpdateSchema,
)

# ------------------------------------------------------
# SUCCESS
# ------------------------------------------------------


class TestTaskSchemasSuccess:

    def test_task_base_schema_valid(self):
        task = TaskBaseSchema(
            title="Test Task",
            description="Some description",
            status=TaskEnum.DONE,
            deadline=datetime.utcnow() + timedelta(days=1),
            is_completed=True,
        )
        assert task.title == "Test Task"
        assert task.status == TaskEnum.DONE
        assert task.is_completed is True

    def test_task_create_schema_valid(self):
        task = TaskCreateSchema(
            title="New Task",
            description="Testing creation",
            deadline=datetime.utcnow() + timedelta(days=2),
        )
        assert task.status == TaskEnum.IN_PROGRESS
        assert task.is_completed is False

    def test_task_update_schema_partial(self):
        task = TaskUpdateSchema(title="Updated Task")
        assert task.title == "Updated Task"
        assert task.description is None
        assert task.status is None

    def test_task_response_schema_valid(self):
        task = TaskResponseSchema(
            id=1,
            user_id=42,
            title="Response Task",
            description="Task for response",
            status=TaskEnum.IN_PROGRESS,
            deadline=datetime.utcnow() + timedelta(days=1),
            is_completed=False,
        )
        assert task.id == 1
        assert task.user_id == 42
        assert task.status == TaskEnum.IN_PROGRESS


# ------------------------------------------------------
# ERRORS
# ------------------------------------------------------


class TestTaskSchemasErrors:

    def test_invalid_enum_status(self):
        with pytest.raises(ValidationError):
            TaskBaseSchema(
                title="Bad Task",
                description="Invalid status",
                status="INVALID",
                deadline=datetime.utcnow() + timedelta(days=1),
                is_completed=False,
            )

    def test_missing_required_fields_in_base_schema(self):
        with pytest.raises(ValidationError):
            TaskBaseSchema(description="No title", deadline=datetime.utcnow())

    def test_invalid_deadline_type(self):
        with pytest.raises(ValidationError):
            TaskBaseSchema(
                title="Deadline Fail",
                description="Invalid deadline type",
                status=TaskEnum.IN_PROGRESS,
                deadline="not-a-datetime",
                is_completed=False,
            )

    def test_missing_required_fields_in_response_schema(self):
        with pytest.raises(ValidationError):
            TaskResponseSchema(
                id=10,
                title="Missing user_id",
                description="Response fail",
                status=TaskEnum.IN_PROGRESS,
                deadline=datetime.utcnow(),
                is_completed=True,
            )

    def test_update_schema_invalid_status(self):
        with pytest.raises(ValidationError):
            TaskUpdateSchema(status="WRONG")
