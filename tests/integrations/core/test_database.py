import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ArgumentError, UnboundExecutionError

from app.core.database import Base, engine, SessionLocal

# pytest tests/integrations/core/test_database.py

class TestDatabaseSuccess:
    def test_engine_instance(self):
        assert isinstance(engine, AsyncEngine)

    def test_session_local_instance(self):
        session = SessionLocal()
        assert isinstance(session, AsyncSession)

    def test_base_declarative(self):
        assert hasattr(Base, "metadata")
        assert Base.metadata is not None


class TestDatabaseErrors:
    def test_invalid_database_url(self, monkeypatch):
        monkeypatch.setenv("DB_TYPE", "invalid_driver")
        from app.core.config import Settings
        s = Settings(_env_file=".env.example")
        from sqlalchemy.ext.asyncio import create_async_engine
        with pytest.raises(ArgumentError):
            create_async_engine(s.DATABASE_URL)

    @pytest.mark.asyncio
    async def test_session_with_invalid_bind(self):
        session = sessionmaker(bind=None, class_=AsyncSession)
        s = session()

        with pytest.raises(UnboundExecutionError):
            await s.execute(text("SELECT 1"))
