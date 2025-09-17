from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException, status

import app.services.auth_service as auth_service
from app.api.auth import auth
from app.schemas.users import UserCreateSchema

# ------------------------------------------------------
# REGISTER
# ------------------------------------------------------


@pytest.mark.asyncio
class TestAuthRegisterCrud:

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

    async def test_register_user_exists_edge(self, test_db, monkeypatch):
        from app.schemas.users import UserCreateSchema
        from app.services import auth_service

        user_data = UserCreateSchema(
            name="Edge", email="edge@example.com", password="password123", role="user"
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


@pytest.mark.asyncio
class TestAuthRegisterErrors:

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
            test_db, "add", AsyncMock(side_effect=Exception("DB error"))
        )
        monkeypatch.setattr(test_db, "commit", AsyncMock())

        with pytest.raises(HTTPException) as exc:
            await auth_service.register_user(user_data, db=test_db)

        assert exc.value.status_code == 500
        assert "internal server error" in exc.value.detail.lower()

    async def test_register_user_commit_error(self, test_db, monkeypatch):
        from app.schemas.users import UserCreateSchema
        from app.services import auth_service

        user_data = UserCreateSchema(
            name="CommitError",
            email="commit_error@example.com",
            password="password123",
            role="user",
        )

        monkeypatch.setattr(test_db, "add", lambda u: None)

        async def raise_commit(*args, **kwargs):
            raise Exception("Commit error")

        monkeypatch.setattr(test_db, "commit", raise_commit)

        with pytest.raises(HTTPException) as exc:
            await auth_service.register_user(user_data, db=test_db)

        assert exc.value.status_code == 500
        assert "internal server error" in exc.value.detail.lower()

    async def test_register_user_refresh_error(self, test_db, monkeypatch):
        user_data = UserCreateSchema(
            name="RefError", email="ref@example.com", password="123", role="user"
        )

        monkeypatch.setattr(test_db, "add", lambda u: None)
        monkeypatch.setattr(test_db, "commit", AsyncMock())
        monkeypatch.setattr(
            test_db, "refresh", AsyncMock(side_effect=Exception("refresh fail"))
        )
        monkeypatch.setattr(test_db, "rollback", AsyncMock())

        with pytest.raises(HTTPException) as exc:
            await auth_service.register_user(user_data, db=test_db)

        assert exc.value.status_code == 500
        assert "internal server error" in exc.value.detail.lower()


# ------------------------------------------------------
# LOGIN json
# ------------------------------------------------------


@pytest.mark.asyncio
class TestAuthLoginCrud:
    async def test_login_success(self, test_client, user_factory, test_db):
        user = user_factory(
            email="login@example.com", password=auth.hash_password("secret")
        )
        test_db.add(user)
        await test_db.commit()

        resp = await test_client.post(
            "/auth/login", json={"email": "login@example.com", "password": "secret"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_hash_and_verify_password_roundtrip(self):
        raw = "mypassword"
        hashed = auth_service.hash_password(raw)

        assert hashed != raw
        assert auth_service.verify_password(raw, hashed)
        assert not auth_service.verify_password("wrong", hashed)

    async def test_get_current_user_success(self, test_db, user_factory):
        user = user_factory(email="current@example.com")
        test_db.add(user)
        await test_db.commit()

        token = auth_service.create_access_token({"sub": user.email})

        result = await auth.get_current_user(token=token, db=test_db)
        assert result.email == "current@example.com"


@pytest.mark.asyncio
class TestAuthLoginErrors:

    async def test_login_invalid_email(self, test_client):
        resp = await test_client.post(
            "/auth/login", json={"email": "nope@example.com", "password": "secret"}
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "User is not found"

    async def test_login_invalid_password(self, test_client, user_factory, test_db):
        user = user_factory(
            email="wrongpass@example.com", password=auth.hash_password("right")
        )
        test_db.add(user)
        await test_db.commit()

        resp = await test_client.post(
            "/auth/login", json={"email": "wrongpass@example.com", "password": "bad"}
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid password"

    async def test_login_blocked_user(self, test_client, user_factory, test_db):
        user = user_factory(
            email="blocked@example.com",
            password=auth.hash_password("pw"),
            is_active=False,
        )
        test_db.add(user)
        await test_db.commit()

        resp = await test_client.post(
            "/auth/login", json={"email": "blocked@example.com", "password": "pw"}
        )

        await test_db.refresh(user)

        assert resp.status_code == 403
        assert resp.json()["detail"] == "User is blocked"

    async def test_login_user_verify_password_crash(
        self, test_db, user_factory, monkeypatch
    ):
        user = user_factory(email="vp@example.com", password="hash")
        test_db.add(user)
        await test_db.commit()

        def fake_verify_password(p, h):
            raise Exception("vp crash")

        monkeypatch.setattr(auth_service, "verify_password", fake_verify_password)

        creds = auth_service.UserAuthSchema(email=user.email, password="123")

        with pytest.raises(Exception) as exc:
            await auth_service.login_user(creds, db=test_db)

        assert "vp crash" in str(exc.value)

    async def test_get_current_user_invalid_token(self, monkeypatch):
        bad_token = "not.a.jwt.token"

        with pytest.raises(HTTPException) as exc:
            await auth.get_current_user(token=bad_token)

        assert exc.value.status_code == 401
        assert "invalid" in exc.value.detail.lower()


# ------------------------------------------------------
# LOGIN (FORM/token)
# ------------------------------------------------------


@pytest.mark.asyncio
class TestAuthLoginTokenCrud:
    async def test_login_token_success(self, test_client, user_factory, test_db):
        user = user_factory(email="form@example.com", password=auth.hash_password("pw"))
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

    async def test_login_token_sets_cookies(self, test_client, user_factory, test_db):
        user = user_factory(
            email="cookie@example.com",
            password=auth_service.hash_password("pw"),
        )
        test_db.add(user)
        await test_db.commit()

        resp = await test_client.post(
            "/auth/token",
            data={"username": "cookie@example.com", "password": "pw"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.cookies
        assert "refresh_token" in resp.cookies
        assert resp.cookies["access_token"] != ""
        assert resp.cookies["refresh_token"] != ""


@pytest.mark.asyncio
class TestAuthLoginTokenErrors:

    async def test_login_token_invalid_user(self, test_client):
        resp = await test_client.post(
            "/auth/token",
            data={"username": "ghost@example.com", "password": "pw"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "User is not found"

    async def test_login_token_blocked_user(self, test_client, user_factory, test_db):
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

    async def test_login_token_invalid_password(
        self, test_client, user_factory, test_db
    ):
        user = user_factory(
            email="wrongpwtoken@example.com", password=auth.hash_password("correct")
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


@pytest.mark.asyncio
class TestAuthRefreshCrud:
    async def test_refresh_success(self, test_client, user_factory, test_db):
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
class TestAuthRefreshErrors:
    async def test_refresh_invalid_token(self, test_client):
        resp = await test_client.post(
            "/auth/refresh", cookies={"refresh_token": "bad.token"}
        )
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Invalid refresh token"

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

    async def test_refresh_token_missing_sub(self, test_client):
        with patch("app.services.auth_service.verify_refresh_token", return_value={}):
            resp = await test_client.post(
                "/auth/refresh", cookies={"refresh_token": "dummy.token"}
            )
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Invalid refresh token"
