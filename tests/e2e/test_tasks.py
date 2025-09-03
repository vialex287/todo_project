# pytest tests/e2e/test_tasks.py

from datetime import datetime, timedelta, timezone

import pytest

from app.schemas.tasks import TaskEnum


@pytest.mark.asyncio
@pytest.mark.e2e
class TestTasksE2E:

    async def test_create_task(self,
                               client,
                               registered_user,
                               user_token):
        response = await client.post(
            f"/{registered_user['id']}/tasks/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Test Task",
                "description": "Task description",
                "status": TaskEnum.IN_PROGRESS.value,
                "deadline": (
                    datetime.now(timezone.utc) + timedelta(days=1)
                ).isoformat(),
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["description"] == "Task description"
        assert data["status"] == TaskEnum.IN_PROGRESS.value
        assert data["is_completed"] is False
        self.task_id = data["id"]

    async def test_get_tasks_from_user(self,
                                       client,
                                       registered_user,
                                       user_token):
        await client.post(
            f"/{registered_user['id']}/tasks/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Task for list",
                "description": "Task description",
                "status": TaskEnum.IN_PROGRESS.value,
                "deadline": (
                    datetime.now(timezone.utc) + timedelta(days=1)
                ).isoformat(),
            },
        )

        response = await client.get(
            f"/{registered_user['id']}/tasks/",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    async def test_get_task_from_user(self,
                                      client,
                                      registered_user,
                                      user_token):
        create_resp = await client.post(
            f"/{registered_user['id']}/tasks/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Get Task",
                "description": "Test get",
                "status": TaskEnum.IN_PROGRESS.value,
                "deadline": (
                    datetime.now(timezone.utc) + timedelta(days=2)
                ).isoformat(),
            },
        )
        task = create_resp.json()
        task_id = task["id"]

        response = await client.get(
            f"/{registered_user['id']}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Get Task"

    async def test_update_task_from_user(self,
                                         client,
                                         registered_user,
                                         user_token):
        create_resp = await client.post(
            f"/{registered_user['id']}/tasks/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Update Task",
                "description": "To update",
                "status": TaskEnum.IN_PROGRESS.value,
                "deadline": (
                    datetime.now(timezone.utc) + timedelta(days=3)
                ).isoformat(),
            },
        )
        task = create_resp.json()
        task_id = task["id"]

        response = await client.put(
            f"/{registered_user['id']}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Updated Task",
                "description": "Updated description",
                "status": TaskEnum.DONE.value,
                "deadline": (
                    datetime.now(timezone.utc) + timedelta(days=4)
                ).isoformat(),
                "is_completed": True,
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["description"] == "Updated description"
        assert data["status"] == TaskEnum.DONE.value
        assert data["is_completed"] is True

    async def test_delete_task_from_user(self,
                                         client,
                                         registered_user,
                                         user_token):
        create_resp = await client.post(
            f"/{registered_user['id']}/tasks/",
            headers={"Authorization": f"Bearer {user_token}"},
            json={
                "title": "Delete Task",
                "description": "To delete",
                "status": TaskEnum.IN_PROGRESS.value,
                "deadline": (
                    datetime.now(timezone.utc) + timedelta(days=5)
                ).isoformat(),
            },
        )
        task = create_resp.json()
        task_id = task["id"]

        response = await client.delete(
            f"/{registered_user['id']}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 204, response.text
