import pytest
from jose import jwt

from app.core.config import settings

# pytest tests/e2e/test_auth.py

@pytest.mark.asyncio
class TestAuthE2E:

    async def test_register(self, client):
        resp = await client.post(
            "/auth/register",
            json={
                "name": "Test",
                "email": "user@example.com",
                "role": "admin",
                "password": "secret123",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert data["email"] == "user@example.com"

    async def test_register_duplicate_email(self, client):
        resp = await client.post(
            "/auth/register",
            json={
                "name": "Test",
                "email": "user@example.com",
                "role": "admin",
                "password": "secret123",
            },
        )
        assert resp.status_code in (400, 409)

    async def test_login_valid_credentials(self, client):
        resp = await client.post(
            "/auth/login",
            json={"email": "user@example.com",
                  "password": "secret123"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

        payload = jwt.decode(
            data["access_token"],
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "user@example.com"

    async def test_login_invalid_password(self, client):
        resp = await client.post(
            "/auth/login",
            json={"email": "user@example.com",
                  "password": "wrongpass"}
        )
        assert resp.status_code == 401
        data = resp.json()
        assert data["detail"] == "Invalid password"

    async def test_refresh_token(self, client):
        resp = await client.post(
            "/auth/login",
            json={"email": "user@example.com",
                  "password": "secret123"}
        )
        tokens = resp.json()

        resp = await client.post(
            "/auth/refresh",
            cookies={"refresh_token": tokens["refresh_token"]}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_logout(self, client):
        resp = await client.post("/auth/logout")
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "Logged out"
