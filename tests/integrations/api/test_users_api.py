import pytest

from app.models.users import User

# ------------------------------------------------------
# CRUD
# ------------------------------------------------------


@pytest.mark.asyncio
class TestUsersCRUD:

    async def test_get_users_as_admin(self, test_client, test_db, user_factory):
        admin = user_factory(role="admin")
        test_db.add(admin)
        await test_db.commit()
        await test_db.refresh(admin)

        test_client.set_current_user(admin)

        resp = await test_client.get("/users/")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)

    async def test_get_user_by_id(self, test_client, test_db, user_factory):
        admin = user_factory(role="admin")
        user = user_factory(role="user", email="user@example.com")
        test_db.add_all([admin, user])
        await test_db.commit()
        await test_db.refresh(admin)
        await test_db.refresh(user)

        test_client.set_current_user(admin)

        resp = await test_client.get(f"/users/{user.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == user.id
        assert data["email"] == "user@example.com"

    async def test_update_user(self, test_client, test_db, user_factory):
        admin = user_factory(role="admin")
        user = user_factory(role="user", email="old@example.com", name="Old Name")
        test_db.add_all([admin, user])
        await test_db.commit()
        await test_db.refresh(admin)
        await test_db.refresh(user)

        test_client.set_current_user(admin)

        payload = {
            "name": "New Name",
            "email": "new@example.com",
            "password": "newpass123",
        }
        resp = await test_client.put(f"/users/{user.id}", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "New Name"
        assert data["email"] == "new@example.com"

    async def test_delete_user(self, test_client, test_db, user_factory):
        admin = user_factory(role="admin")
        user = user_factory(role="user")
        test_db.add_all([admin, user])
        await test_db.commit()
        await test_db.refresh(admin)
        await test_db.refresh(user)

        test_client.set_current_user(admin)

        resp = await test_client.delete(f"/users/{user.id}")
        assert resp.status_code == 204

        deleted = await test_db.get(User, user.id)
        assert deleted is None


# ------------------------------------------------------
# AUTH
# ------------------------------------------------------


@pytest.mark.asyncio
class TestUsersAuth:

    async def test_get_users_as_regular_user(self, test_client, test_db, user_factory):
        user = user_factory(role="user")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        test_client.set_current_user(user)

        resp = await test_client.get("/users/")
        assert resp.status_code == 403

    async def test_user_cannot_delete_other_user(
        self, test_client, test_db, user_factory
    ):
        user1 = user_factory(role="user")
        user2 = user_factory(role="user")
        test_db.add_all([user1, user2])
        await test_db.commit()
        await test_db.refresh(user1)
        await test_db.refresh(user2)

        test_client.set_current_user(user1)

        resp = await test_client.delete(f"/users/{user2.id}")
        assert resp.status_code == 403

    async def test_user_can_update_self(self, test_client, test_db, user_factory):
        user = user_factory(role="user", email="me@example.com", name="Me")
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)

        test_client.set_current_user(user)

        payload = {"name": "Updated Me", "email": "me_new@example.com"}
        resp = await test_client.put(f"/users/{user.id}", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Updated Me"
        assert data["email"] == "me_new@example.com"

    async def test_user_cannot_update_other(self, test_client, test_db, user_factory):
        user1 = user_factory(role="user", email="u1@example.com")
        user2 = user_factory(role="user", email="u2@example.com")
        test_db.add_all([user1, user2])
        await test_db.commit()
        await test_db.refresh(user1)
        await test_db.refresh(user2)

        test_client.set_current_user(user1)

        payload = {"name": "Hack", "email": "hack@example.com"}
        resp = await test_client.put(f"/users/{user2.id}", json=payload)
        assert resp.status_code == 403

    async def test_user_cannot_delete_other(self, test_client, test_db, user_factory):
        user1 = user_factory(role="user", email="u1@example.com")
        user2 = user_factory(role="user", email="u2@example.com")
        test_db.add_all([user1, user2])
        await test_db.commit()
        await test_db.refresh(user1)
        await test_db.refresh(user2)

        test_client.set_current_user(user1)

        resp = await test_client.delete(f"/users/{user2.id}")
        assert resp.status_code == 403


# ------------------------------------------------------
# ERRORS
# ------------------------------------------------------


@pytest.mark.asyncio
class TestUsersErrors:

    async def test_get_user_not_found(self, test_client, test_db, user_factory):
        admin = user_factory(role="admin")
        test_db.add(admin)
        await test_db.commit()
        await test_db.refresh(admin)

        test_client.set_current_user(admin)

        resp = await test_client.get("/users/9999")
        assert resp.status_code == 404

    async def test_update_user_not_found(self, test_client, test_db, user_factory):
        admin = user_factory(role="admin")
        test_db.add(admin)
        await test_db.commit()
        await test_db.refresh(admin)

        test_client.set_current_user(admin)

        payload = {"name": "Ghost", "email": "ghost@example.com", "password": "xxx"}
        resp = await test_client.put("/users/9999", json=payload)
        assert resp.status_code == 404

    async def test_delete_user_not_found(self, test_client, test_db, user_factory):
        admin = user_factory(role="admin")
        test_db.add(admin)
        await test_db.commit()
        await test_db.refresh(admin)

        test_client.set_current_user(admin)

        resp = await test_client.delete("/users/9999")
        assert resp.status_code == 404

    async def test_update_user_invalid_email(self, test_client, test_db, user_factory):
        admin = user_factory(role="admin")
        user = user_factory(role="user", email="valid@example.com")
        test_db.add_all([admin, user])
        await test_db.commit()
        await test_db.refresh(admin)
        await test_db.refresh(user)

        test_client.set_current_user(admin)

        payload = {"name": "BadEmail", "email": "invalid-email"}
        resp = await test_client.put(f"/users/{user.id}", json=payload)
        assert resp.status_code == 422
