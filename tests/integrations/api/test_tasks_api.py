from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.models.tasks import Task
from app.schemas.tasks import TaskEnum

# ------------------------------------------------------
# CRUD
# ------------------------------------------------------


@pytest.mark.asyncio
class TestTasksCreate:
    async def test_create_task(self, test_client, test_db, user_factory):
        user = user_factory()
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        payload = {
            "title": "Test Task",
            "description": "This is a test task",
            "status": "In progress",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        }

        resp = await test_client.post(f"/{user.id}/tasks/", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Test Task"
        assert data["status"] == TaskEnum.IN_PROGRESS
        assert data["user_id"] == user.id


@pytest.mark.asyncio
class TestTasksRead:
    async def test_get_tasks_empty(self, test_client, test_db, user_factory):
        user = user_factory()
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        resp = await test_client.get(f"/{user.id}/tasks/")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert data == {"message": "User list is empty"}

    async def test_get_tasks_with_items(
        self, test_client, test_db, user_factory, task_factory
    ):
        user = user_factory()
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        task1 = task_factory(user_id=user.id, title="Task 1")
        task2 = task_factory(user_id=user.id, title="Task 2")

        test_db.add_all([task1, task2])
        await test_db.commit()
        await test_db.refresh(user)
        await test_db.refresh(task1)
        await test_db.refresh(task2)

        resp = await test_client.get(f"/{user.id}/tasks/")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2
        assert {t["title"] for t in data} == {"Task 1", "Task 2"}

    async def test_get_single_task(
        self, test_client, test_db, user_factory, task_factory
    ):
        user = user_factory()
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        task = task_factory(user_id=user.id, title="Sample Task")
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)

        resp = await test_client.get(f"/{user.id}/tasks/{task.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == task.id
        assert data["title"] == "Sample Task"


@pytest.mark.asyncio
class TestTasksUpdate:
    async def test_update_task(self, test_client, test_db, user_factory, task_factory):
        user = user_factory()
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        task = task_factory(user_id=user.id, title="Old Title")
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)

        payload = {
            "title": "New Title",
            "description": "Updated description",
            "deadline": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
            "is_completed": True,
        }

        resp = await test_client.put(f"/{user.id}/tasks/{task.id}", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "New Title"
        assert data["is_completed"] is True
        assert data["status"] == TaskEnum.DONE


@pytest.mark.asyncio
class TestTasksDelete:
    async def test_delete_task(self, test_client, test_db, user_factory, task_factory):
        user = user_factory(role="admin")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        task = task_factory(user_id=user.id, title="Old Title")
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)

        resp = await test_client.delete(f"/{user.id}/tasks/{task.id}")
        assert resp.status_code == 204

        result = await test_db.execute(select(Task).filter(Task.id == task.id))
        deleted_task = result.scalar_one_or_none()
        assert deleted_task is None


# ------------------------------------------------------
# ERRORS
# ------------------------------------------------------


@pytest.mark.asyncio
class TestTasksErrors:

    async def test_create_task_db_error(
        self, test_db, user_factory, task_factory, monkeypatch
    ):
        user = user_factory()
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        payload = task_factory(user_id=user.id)

        monkeypatch.setattr(
            payload, "update_status", lambda: (_ for _ in ()).throw(Exception("boom"))
        )

        from app.schemas.tasks import TaskCreateSchema
        from app.services import tasks_service

        task_data = TaskCreateSchema(
            title=payload.title,
            description=payload.description,
            status=payload.status,
            deadline=datetime.now(timezone.utc) + timedelta(days=1),
        )
        from unittest.mock import patch

        with patch(
            "app.models.tasks.Task.update_status", side_effect=Exception("boom")
        ):
            with pytest.raises(HTTPException) as exc:
                await tasks_service.create_task_user(user.id, task_data, db=test_db)

        assert exc.value.status_code == 500

    async def test_create_task_with_invalid_deadline(
        self, test_client, user_factory, test_db
    ):
        user = user_factory()
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        payload = {
            "title": "Bad Task",
            "description": "some desc",
            "deadline": "not-a-date",
        }

        resp = await test_client.post(f"/{user.id}/tasks/", json=payload)
        assert resp.status_code == 422

        errors = [err["msg"] for err in resp.json()["detail"]]
        assert any("valid datetime" in msg for msg in errors)

    async def test_get_task_from_wrong_user(
        self, test_client, test_db, user_factory, task_factory
    ):
        user1 = user_factory()
        user2 = user_factory()
        test_db.add_all([user1, user2])
        await test_db.commit()
        await test_db.refresh(user1)
        await test_db.refresh(user2)

        task = task_factory(user_id=user1.id, title="Secret task")
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)

        resp = await test_client.get(f"/{user2.id}/tasks/{task.id}")
        assert resp.status_code in (403, 404)

    async def test_update_nonexistent_task(self, test_db, test_client, user_factory):
        user = user_factory(role="admin")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        resp = await test_client.put(
            f"/{user.id}/tasks/99999",
            json={
                "title": "Should Fail",
                "description": "test",
            },
        )

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Task is not found"

    async def test_update_task_db_error(
        self, test_db, user_factory, task_factory, monkeypatch
    ):
        user = user_factory()
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        task = task_factory(user_id=user.id)
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)

        from app.schemas.tasks import TaskUpdateSchema
        from app.services import tasks_service

        new_data = TaskUpdateSchema(title="Updated Title")

        monkeypatch.setattr(
            test_db, "commit", lambda: (_ for _ in ()).throw(Exception("boom"))
        )

        with pytest.raises(HTTPException) as exc:
            await tasks_service.update_task_from_user(
                user.id, task.id, new_data, db=test_db
            )

        assert exc.value.status_code == 500

    async def test_delete_task_wrong_user(
        self, test_client, test_db, user_factory, task_factory
    ):
        user1 = user_factory()
        user2 = user_factory()
        test_db.add_all([user1, user2])
        await test_db.commit()
        await test_db.refresh(user1)
        await test_db.refresh(user2)

        task = task_factory(user_id=user1.id)
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)

        resp = await test_client.delete(f"/{user2.id}/tasks/{task.id}")
        assert resp.status_code in (403, 404)

    async def test_delete_task_db_error(
        self, test_db, user_factory, task_factory, monkeypatch
    ):
        user = user_factory()
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        task = task_factory(user_id=user.id)
        test_db.add(task)
        await test_db.commit()
        await test_db.refresh(task)

        from app.services import tasks_service

        monkeypatch.setattr(
            test_db, "commit", lambda: (_ for _ in ()).throw(Exception("boom"))
        )

        with pytest.raises(HTTPException) as exc:
            await tasks_service.delete_task_from_user(user.id, task.id, db=test_db)

        assert exc.value.status_code == 500
