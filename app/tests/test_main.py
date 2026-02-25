"""Tests for app/main.py FastAPI application."""

from __future__ import annotations

from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_root_returns_correct_structure() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert data["docs"] == "/docs"


async def test_docs_endpoint_is_accessible() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/docs")
    assert response.status_code == 200


async def test_openapi_schema_is_accessible() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "info" in data


async def test_cors_headers_present_for_allowed_origin() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert (
        response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    )
