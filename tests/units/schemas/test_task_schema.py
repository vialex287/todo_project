import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas.tasks import TaskResponseSchema, TaskUpdateSchema, TaskCreateSchema, TaskEnum

# pytest tests\units\schemas\test_task_schema.py -v


class TestTaskCreateSchema:

    def test_valid(self):
        data = {
            "title": "Test Task",
            "description": "Test description",
            "deadline": datetime(2025, 12, 31, 23, 59),
            "status": TaskEnum.IN_PROGRESS,
            "is_completed": False
        }

        schema = TaskCreateSchema(**data)
        assert schema.title == "Test Task"
        assert schema.description == "Test description"
        assert schema.deadline == datetime(2025, 12, 31, 23, 59)
        assert schema.status == TaskEnum.IN_PROGRESS
        assert schema.is_completed is False

    def test_default_values(self):
        data = {
            "title": "Test Task",
            "description": "Test description",
            "deadline": datetime(2025, 12, 31)
        }

        schema = TaskCreateSchema(**data)
        assert schema.status == TaskEnum.IN_PROGRESS
        assert schema.is_completed is False

    # errors #

    def test_missing_title(self):
        with pytest.raises(ValidationError):
            TaskCreateSchema(
                description="Test",
                deadline=datetime(2025, 12, 31)
            )

    def test_missing_deadline(self):
        with pytest.raises(ValidationError):
            TaskCreateSchema(
                title="Test",
                description="Test"
            )

    def test_invalid_fields(self):
        data = {
            "title": "Test Task",
            "description": "Test description",
            "deadline": "lalala",
            "status": TaskEnum.EXPIRED,
            "is_completed": 3
        }

        with pytest.raises(ValidationError):
            TaskCreateSchema(**data)

    def test_invalid_status(self):
        data = {
            "user_id": 123,
            "title": "Test Task",
            "description": "Test description",
            "status": "INVALID_STATUS",
            "deadline": datetime(2024, 12, 31),
            "is_completed": False,
        }

        with pytest.raises(ValidationError):
            TaskCreateSchema(**data)

    def test_invalid_deadline(self):
        data = {
            "user_id": 123,
            "title": "Test Task",
            "description": "Test description",
            "status": TaskEnum.IN_PROGRESS,
            "deadline": "not-a-datetime",
            "is_completed": False
        }

        with pytest.raises(ValidationError):
            TaskCreateSchema(**data)

    def test_invalid_is_completed(self):
        data = {
            "user_id": 123,
            "title": "Test Task",
            "description": "Test description",
            "status": TaskEnum.IN_PROGRESS,
            "deadline": datetime(2024, 12, 31),
            "is_completed": "not-a-boolean"
        }

        with pytest.raises(ValidationError):
            TaskCreateSchema(**data)


class TestTaskUpdateSchema:
    def test_update_empty(self):
        schema = TaskUpdateSchema()
        assert schema.title is None
        assert schema.description is None
        assert schema.status is None
        assert schema.deadline is None

    def test_update_only_title(self):
        schema = TaskUpdateSchema(title="New Title")
        assert schema.title == "New Title"
        assert schema.description is None
        assert schema.status is None

    def test_update_all_fields(self):
        new_deadline = datetime(2024, 12, 31)

        schema = TaskUpdateSchema(
            title="New Title",
            description="New description",
            status=TaskEnum.EXPIRED,
            deadline=new_deadline,
        )

        assert schema.title == "New Title"
        assert schema.description == "New description"
        assert schema.status == TaskEnum.EXPIRED
        assert schema.deadline == new_deadline

    # errors #

    def test_update_invalid_status(self):
        with pytest.raises(ValidationError):
            TaskUpdateSchema(status="INVALID_STATUS")

    def test_update_invalid_deadline(self):
        with pytest.raises(ValidationError):
            TaskUpdateSchema(status="INVALID_STATUS")


class TestTaskResponseSchema:

    def test_valid_data(self):
        data = {
            "id": 1,
            "user_id": 123,
            "title": "Test Task",
            "description": "Test description",
            "status": TaskEnum.DONE,
            "deadline": datetime(2025, 12, 31, 23, 59),
            "is_completed": True
        }

        schema = TaskResponseSchema(**data)
        assert schema.id == 1
        assert schema.user_id == 123
        assert schema.title == "Test Task"
        assert schema.description == "Test description"
        assert schema.status == TaskEnum.DONE
        assert schema.deadline == datetime(2025, 12, 31, 23, 59)
        assert schema.is_completed is True

    def test_default_values(self):
        data = {
            "id": 1,
            "user_id": 123,
            "title": "Test Task",
            "description": "Test description",
            "deadline": datetime(2024, 12, 31)
        }

        schema = TaskResponseSchema(**data)
        assert schema.status == TaskEnum.IN_PROGRESS
        assert schema.is_completed is False

    def test_response_from_attributes(self):
        class MockTask:
            def __init__(self):
                self.id = 1
                self.user_id = 123
                self.title = "Task"
                self.description = "description"
                self.status = TaskEnum.IN_PROGRESS
                self.deadline = datetime(2025, 12, 31)
                self.is_completed = False

        mock_task = MockTask()
        schema = TaskResponseSchema.model_validate(mock_task)

        assert schema.id == 1
        assert schema.user_id == 123
        assert schema.title == "Task"
        assert schema.description == "description"
        assert schema.deadline == datetime(2025, 12, 31)
        assert schema.status == TaskEnum.IN_PROGRESS
        assert schema.is_completed is False

    # errors

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            TaskResponseSchema(
                user_id=123,
                title="Test",
                description="Test",
                deadline=datetime(2024, 12, 31)
            )

    def test_missing_user_id(self):
        with pytest.raises(ValidationError):
            TaskResponseSchema(
                id=1,
                title="Test",
                description="Test",
                deadline=datetime(2024, 12, 31)
            )

    def test_missing_title(self):
        with pytest.raises(ValidationError):
            TaskResponseSchema(
                id=1,
                user_id=123,
                description="Test",
                deadline=datetime(2024, 12, 31)
            )

    def test_missing_deadline(self):
        with pytest.raises(ValidationError):
            TaskResponseSchema(
                id=1,
                user_id=123,
                title="Test",
                description="Test"
            )


    def test_invalid_status(self):
        data = {
            "id": 1,
            "user_id": 123,
            "title": "Test Task",
            "description": "Test description",
            "status": "INVALID_STATUS",
            "deadline": datetime(2024, 12, 31),
            "is_completed": False,
        }

        with pytest.raises(ValidationError):
            TaskResponseSchema(**data)

    def test_invalid_deadline(self):
        data = {
            "id": 1,
            "user_id": 123,
            "title": "Test Task",
            "description": "Test description",
            "status": TaskEnum.IN_PROGRESS,
            "deadline": "not-a-datetime",
            "is_completed": False
        }

        with pytest.raises(ValidationError):
            TaskResponseSchema(**data)

    def test_invalid_is_completed(self):
        data = {
            "id": 1,
            "user_id": 123,
            "title": "Test Task",
            "description": "Test description",
            "status": TaskEnum.IN_PROGRESS,
            "deadline": datetime(2024, 12, 31),
            "is_completed": "not-a-boolean"
        }

        with pytest.raises(ValidationError):
            TaskResponseSchema(**data)


















