"""Integration tests for database connectivity.

Requires a real PostgreSQL database at settings.database_url.
Run with: pytest -v -m integration
Skip with: pytest -v -m "not integration"
"""

from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

pytestmark = pytest.mark.integration


async def test_database_connection(test_db_session: AsyncSession) -> None:
    """Verify the database accepts queries."""
    result = await test_db_session.execute(text("SELECT 1"))
    row = result.fetchone()
    assert row is not None
    assert row[0] == 1


async def test_session_executes_queries(test_db_session: AsyncSession) -> None:
    """Verify session can run multiple queries."""
    result = await test_db_session.execute(text("SELECT current_database()"))
    row = result.fetchone()
    assert row is not None
    assert isinstance(row[0], str)


async def test_base_metadata_is_configured(test_db_session: AsyncSession) -> None:
    """Verify Base.metadata is accessible (needed for schema operations)."""
    assert Base.metadata is not None
