"""Health check endpoints.

Endpoints are registered WITHOUT a prefix so they live at the root path:
    GET /health       — API process is running
    GET /health/db    — database connection is available
    GET /health/ready — all dependencies healthy and ready for traffic
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.logging import get_logger

logger = get_logger("app.core.health")

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Confirm the API process is running."""
    return {"status": "healthy", "service": "api"}


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db)) -> dict[str, str]:  # noqa: B008
    """Confirm the database connection is available."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("database.health_check_failed", exc_info=True)
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "healthy", "service": "database", "provider": "postgresql"}


@router.get("/health/ready")
async def health_ready(
    db: AsyncSession = Depends(get_db),  # noqa: B008
    settings: Settings = Depends(get_settings),  # noqa: B008
) -> dict[str, str]:
    """Confirm all dependencies are ready for traffic."""
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("database.health_check_failed", exc_info=True)
        raise HTTPException(status_code=503, detail="Database not ready") from exc
    return {
        "status": "ready",
        "environment": settings.environment,
        "database": "connected",
    }
