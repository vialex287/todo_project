from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.dependencies import task_valid, user_valid, validate_email


class TestUserValid:

    @pytest.mark.asyncio
    async def test_user_valid_with_user(self):
        mock_user = MagicMock()

        result = await user_valid(mock_user)
        assert isinstance(result, bool)
        assert result is True

    @pytest.mark.asyncio
    async def test_user_valid_without_user(self):
        with pytest.raises(HTTPException) as exc_info:
            await user_valid(None)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "User is not found"


class TestTaskValid:
    @pytest.mark.asyncio
    async def test_task_valid_with_task(self):
        mock_task = MagicMock()

        result = await task_valid(mock_task)
        assert isinstance(result, bool)
        assert result is True

    @pytest.mark.asyncio
    async def test_task_valid_without_task(self):
        with pytest.raises(HTTPException) as exc_info:
            await task_valid(None)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Task is not found"


class TestValidateEmail:
    def test_validate_email_valid(self):
        result = validate_email("test@example.com")
        assert result == "test@example.com"

    def test_validate_email_valid_special_chars(self):
        result = validate_email("test.user+tag@example.com")
        assert result == "test.user+tag@example.com"

    def test_validate_email_none(self):
        result = validate_email(None)
        assert result is None

    def test_validate_email_valid_with_subdomain(self):
        result = validate_email("test@sub.example.com")
        assert result == "test@sub.example.com"

    # errrors #

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "invalid-email",
            "test@",
            "test@example",
            "test @example.com",
            "",
            "test@@example.com",
        ],
    )
    def test_validate_email_invalid(self, invalid_email):
        with pytest.raises(ValueError, match="Invalid email format"):
            validate_email(invalid_email)
