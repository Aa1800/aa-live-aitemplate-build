"""FastAPI application entry point.

Run with: uv run uvicorn app.main:app --reload --port 8123
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.database import engine
from app.core.exceptions import setup_exception_handlers
from app.core.health import router as health_router
from app.core.logging import get_logger, setup_logging
from app.core.middleware import setup_middleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Configure logging and announce startup/shutdown."""
    setup_logging(log_level=settings.log_level)
    logger = get_logger("app.main")
    logger.info("application.startup", environment=settings.environment)
    logger.info("database.connection.initialized")
    yield
    await engine.dispose()
    logger.info("database.connection.closed")
    logger.info("application.shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
)

setup_middleware(app)
setup_exception_handlers(app)
app.include_router(health_router)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint — confirms the API is running."""
    return {
        "message": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8123, reload=True)  # noqa: S104
