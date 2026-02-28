"""Tests for health check endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.main import app


@pytest.fixture
def mock_db(monkeypatch: pytest.MonkeyPatch):
    """Override get_db dependency with a mock AsyncSession."""
    session = AsyncMock(spec=AsyncSession)

    async def override() -> object:
        yield session

    app.dependency_overrides[get_db] = override
    yield session
    app.dependency_overrides.clear()


async def test_health_returns_200_without_db() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "api"


async def test_health_db_returns_200_when_connected(mock_db: AsyncMock) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "database"
    assert data["provider"] == "postgresql"


async def test_health_db_returns_503_when_db_fails(mock_db: AsyncMock) -> None:
    mock_db.execute.side_effect = Exception("connection refused")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/db")
    assert response.status_code == 503


async def test_health_ready_returns_200_when_ready(mock_db: AsyncMock) -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "environment" in data
    assert data["database"] == "connected"


async def test_health_ready_returns_503_when_db_fails(mock_db: AsyncMock) -> None:
    mock_db.execute.side_effect = Exception("connection refused")
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health/ready")
    assert response.status_code == 503
