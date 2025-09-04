import pytest
from pydantic_core import ValidationError

from app.core.config import Settings


class TestConfig:
    def test_settings_fields(self, test_settings):
        s = test_settings
        assert isinstance(s.DB_TYPE, str)
        assert isinstance(s.DB_USER, str)
        assert isinstance(s.DB_PASSWORD, str)
        assert isinstance(s.DB_HOST, str)
        assert isinstance(s.DB_PORT, int)
        assert isinstance(s.DB_NAME, str)
        assert isinstance(s.SECRET_KEY, str)
        assert isinstance(s.PASSWORD_SALT, str)
        assert isinstance(s.ALGORITHM, str)
        assert isinstance(s.ACCESS_TOKEN_EXPIRE_MINUTES, int)

    def test_database_url_property(self, test_settings):
        s = test_settings
        url = s.DATABASE_URL
        assert url.startswith(s.DB_TYPE)

        if not s.DB_TYPE.startswith("sqlite"):
            assert s.DB_USER in url
            assert s.DB_PASSWORD in url
            assert s.DB_HOST in url
        assert s.DB_NAME in url

    def test_wrong_port_type(self, monkeypatch):
        monkeypatch.setenv("DB_PORT", "not_a_number")
        with pytest.raises(ValidationError):
            _ = Settings(_env_file=".env.example")
