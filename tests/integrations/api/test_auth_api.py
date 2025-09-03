from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException, status

from app.api.auth import auth

# pytest tests/integrations/api/test_auth_api.py

# ------------------------------------------------------
# REGISTER
# ------------------------------------------------------


class TestAuthRegisterCrud:

    @pytest.mark.asyncio
    async def test_register_user_success(self, test_client):
        resp = await test_client.post(
            "/auth/register",
            json={
                "name": "Alice",
                "email": "alice@example.com",
                "password": "password123",
                "role": "user",
            },
        )
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert data["email"] == "alice@example.com"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_user_exists_edge(self, test_db, monkeypatch):
        from app.schemas.users import UserCreateSchema
        from app.services import auth_service

        user_data = UserCreateSchema(
            name="Edge",
            email="edge@example.com",
            password="password123",
            role="user"
        )

        class FakeResult:
            def scalars(self):
                return self

            def first(self):
                return True

        async def fake_execute(*args, **kwargs):
            return FakeResult()

        monkeypatch.setattr(test_db, "execute", fake_execute)

        with pytest.raises(HTTPException) as exc:
            await auth_service.register_user(user_data, db=test_db)

        assert exc.value.status_code == 409
        assert "already exist" in exc.value.detail.lower()


class TestAuthRegisterErrors:

    @pytest.mark.asyncio
    async def test_register_user_already_exists(
        self, test_client, user_factory, test_db
    ):
        user = user_factory(email="bob@example.com")
        test_db.add(user)
        await test_db.commit()

        resp = await test_client.post(
            "/auth/register",
            json={
                "name": "Bob",
                "email": "bob@example.com",
                "password": "password123",
                "role": "user",
            },
        )
        assert resp.status_code == 409
        assert resp.json()["detail"] == "Email already exist"

    @pytest.mark.asyncio
    async def test_register_user_db_error(self, test_db, monkeypatch):
        from app.schemas.users import UserCreateSchema
        from app.services import auth_service

        user_data = UserCreateSchema(
            name="ErrorUser",
            email="error@example.com",
            password="password123",
            role="user",
        )

        monkeypatch.setattr(
            test_db, "add",
            AsyncMock(side_effect=Exception("DB error"))
        )
        monkeypatch.setattr(test_db, "commit", AsyncMock())

        with pytest.raises(HTTPException) as exc:
            await auth_service.register_user(user_data, db=test_db)

        assert exc.value.status_code == 500
        assert "internal server error" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_register_user_commit_error(self, test_db, monkeypatch):
        from app.schemas.users import UserCreateSchema
        from app.services import auth_service

        user_data = UserCreateSchema(
            name="CommitError",
            email="commit_error@example.com",
            password="password123",
            role="user",
        )

        # db.add работает нормально
        monkeypatch.setattr(test_db, "add", lambda u: None)

        # db.commit вызывает исключение
        async def raise_commit(*args, **kwargs):
            raise Exception("Commit error")

        monkeypatch.setattr(test_db, "commit", raise_commit)

        with pytest.raises(HTTPException) as exc:
            await auth_service.register_user(user_data, db=test_db)

        assert exc.value.status_code == 500
        assert "internal server error" in exc.value.detail.lower()


# ------------------------------------------------------
# LOGIN json
# ------------------------------------------------------


class TestAuthLoginCrud:
    @pytest.mark.asyncio
    async def test_login_success(self, test_client, user_factory, test_db):
        user = user_factory(
            email="login@example.com",
            password=auth.hash_password("secret")
        )
        test_db.add(user)
        await test_db.commit()

        resp = await test_client.post(
            "/auth/login",
            json={"email": "login@example.com", "password": "secret"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data


class TestAuthLoginErrors:
    @pytest.mark.asyncio
    async def test_login_invalid_email(self, test_client):
        resp = await test_client.post(
            "/auth/login",
            json={"email": "nope@example.com", "password": "secret"}
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "User is not found"

    @pytest.mark.asyncio
    async def test_login_invalid_password(self,
                                          test_client,
                                          user_factory,
                                          test_db):
        user = user_factory(
            email="wrongpass@example.com",
            password=auth.hash_password("right")
        )
        test_db.add(user)
        await test_db.commit()

        resp = await test_client.post(
            "/auth/login",
            json={"email": "wrongpass@example.com", "password": "bad"}
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid password"

    @pytest.mark.asyncio
    async def test_login_blocked_user(self,
                                      test_client,
                                      user_factory,
                                      test_db):
        user = user_factory(
            email="blocked@example.com",
            password=auth.hash_password("pw"),
            is_active=False,
        )
        test_db.add(user)
        await test_db.commit()

        resp = await test_client.post(
            "/auth/login",
            json={"email": "blocked@example.com", "password": "pw"}
        )

        await test_db.refresh(user)

        assert resp.status_code == 403
        assert resp.json()["detail"] == "User is blocked"


# ------------------------------------------------------
# LOGIN (FORM/token)
# ------------------------------------------------------


class TestAuthLoginTokenCrud:
    @pytest.mark.asyncio
    async def test_login_token_success(self,
                                       test_client,
                                       user_factory,
                                       test_db):
        user = user_factory(email="form@example.com",
                            password=auth.hash_password("pw"))
        test_db.add(user)
        await test_db.commit()

        resp = await test_client.post(
            "/auth/token",
            data={"username": "form@example.com", "password": "pw"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.cookies
        assert "refresh_token" in resp.cookies


class TestAuthLoginTokenErrors:
    @pytest.mark.asyncio
    async def test_login_token_invalid_user(self, test_client):
        resp = await test_client.post(
            "/auth/token",
            data={"username": "ghost@example.com", "password": "pw"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "User is not found"

    @pytest.mark.asyncio
    async def test_login_token_blocked_user(self,
                                            test_client,
                                            user_factory,
                                            test_db):
        user = user_factory(
            email="blockedtoken@example.com",
            password=auth.hash_password("pw"),
            is_active=False,
        )
        test_db.add(user)
        await test_db.commit()

        resp = await test_client.post(
            "/auth/token",
            data={"username": "blockedtoken@example.com", "password": "pw"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert resp.status_code == 401
        assert resp.json()["detail"] == "User is blocked"

    @pytest.mark.asyncio
    async def test_login_token_invalid_password(
        self, test_client, user_factory, test_db
    ):
        user = user_factory(
            email="wrongpwtoken@example.com",
            password=auth.hash_password("correct")
        )
        test_db.add(user)
        await test_db.commit()

        resp = await test_client.post(
            "/auth/token",
            data={"username": "wrongpwtoken@example.com", "password": "bad"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid password"


# ------------------------------------------------------
# REFRESH
# ------------------------------------------------------


class TestAuthRefreshCrud:
    @pytest.mark.asyncio
    async def test_refresh_success(self,
                                   test_client,
                                   user_factory,
                                   test_db):
        user = user_factory(
            email="refresh@example.com", password=auth.hash_password("pw")
        )
        test_db.add(user)
        await test_db.commit()

        refresh = auth.create_refresh_token({"sub": user.email})
        resp = await test_client.post(
            "/auth/refresh", cookies={"refresh_token": refresh}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["message"] == "Refresh token is valid"

    @pytest.mark.asyncio
    async def test_refresh_token_missing_sub(self, test_client):
        with patch("app.services.auth_service.verify_refresh_token",
                   return_value={}):
            resp = await test_client.post(
                "/auth/refresh", cookies={"refresh_token": "dummy.token"}
            )
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Invalid refresh token"

    @pytest.mark.asyncio
    async def test_refresh_token_verify_exception(self, test_client):
        from unittest.mock import patch

        with patch(
            "app.services.auth_service.verify_refresh_token",
            side_effect=Exception("boom"),
        ):
            resp = await test_client.post(
                "/auth/refresh", cookies={"refresh_token": "dummy.token"}
            )
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Invalid refresh token"


class TestAuthRefreshErrors:
    @pytest.mark.asyncio
    async def test_refresh_invalid_token(self, test_client):
        resp = await test_client.post(
            "/auth/refresh", cookies={"refresh_token": "bad.token"}
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid refresh token"
