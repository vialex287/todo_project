import pytest

from app.core.config import Settings


@pytest.fixture
def test_settings():
    return Settings(_env_file=".env.example")
