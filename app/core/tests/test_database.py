"""Tests for app/core/database.py."""

from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core import database as db_module


async def test_engine_is_not_none() -> None:
    assert db_module.engine is not None


async def test_engine_is_async_engine() -> None:
    assert isinstance(db_module.engine, AsyncEngine)


async def test_base_metadata_is_accessible() -> None:
    assert db_module.Base.metadata is not None


async def test_get_db_is_async_generator() -> None:
    gen = db_module.get_db()
    assert inspect.isasyncgen(gen)
    await gen.aclose()


async def test_get_db_yields_async_session() -> None:
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.close = AsyncMock()

    with patch.object(
        db_module,
        "AsyncSessionLocal",
        return_value=_make_async_context_manager(mock_session),
    ):
        gen = db_module.get_db()
        session = await gen.__anext__()
        assert session is mock_session
        await gen.aclose()


def _make_async_context_manager(value: AsyncSession) -> object:
    """Return an object usable as `async with ... as value`."""

    class _CM:
        async def __aenter__(self) -> AsyncSession:
            return value

        async def __aexit__(self, *args: object) -> None:
            pass

    return _CM()
