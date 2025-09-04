import pytest

# pytest tests/e2e/test_users.py


class TestUsersAdminE2E:

    @pytest.mark.asyncio
    async def test_get_users_list(self, client, admin_token):
        resp = await client.get(
            "/users/", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client, admin_token, registered_user):
        resp = await client.get(
            f"/users/{registered_user['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == registered_user["email"]

    @pytest.mark.asyncio
    async def test_update_user_role(self, client, admin_token, registered_user):
        resp = await client.put(
            f"/users/{registered_user['id']}",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

    @pytest.mark.asyncio
    async def test_delete_user(self, client, admin_token, registered_user):
        resp = await client.delete(
            f"/users/{registered_user['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 204


class TestUsersUserE2E:

    @pytest.mark.asyncio
    async def test_get_users_list_forbidden(self, client, user_token):
        resp = await client.get(
            "/users/", headers={"Authorization": f"Bearer {user_token}"}
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_get_other_user_forbidden(self, client, user_token, registered_admin):
        resp = await client.get(
            f"/users/{registered_admin['id']}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_update_self(self, client, user_token, registered_user):
        resp = await client.put(
            f"/users/{registered_user['id']}",
            json={"name": "Alice Updated"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Alice Updated"

    @pytest.mark.asyncio
    async def test_update_self_forbidden_role_change(
        self, client, user_token, registered_user
    ):
        resp = await client.put(
            f"/users/{registered_user['id']}",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_self(self, client, user_token, registered_user):
        resp = await client.delete(
            f"/users/{registered_user['id']}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp.status_code == 204
