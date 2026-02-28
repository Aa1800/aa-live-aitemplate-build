"""Shared fixtures for app/tests/ integration tests.

These fixtures require a real PostgreSQL database.
Run integration tests with: pytest -v -m integration
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


@pytest.fixture
async def test_db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a fresh async engine for the test, dispose on teardown."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_db_session(
    test_db_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh AsyncSession per test, rolling back on teardown."""
    session_factory = async_sessionmaker(test_db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()
