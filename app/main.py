"""FastAPI application entry point.

Run with: uv run uvicorn app.main:app --reload --port 8123
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.core.middleware import setup_middleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Configure logging and announce startup/shutdown."""
    setup_logging(log_level=settings.log_level)
    logger = get_logger("app.main")
    logger.info("application.startup", environment=settings.environment)
    yield
    logger.info("application.shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
)

setup_middleware(app)


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint — confirms the API is running."""
    return {
        "message": settings.app_name,
        "version": settings.version,
        "docs": "/docs",
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8123, reload=True)
