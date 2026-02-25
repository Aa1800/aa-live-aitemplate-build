# ============================================================
# Builder stage — install deps and sync project into .venv
# ============================================================
FROM python:3.12-slim-bookworm AS builder

# Copy uv from the official distroless image (avoids installing via curl)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Compile bytecode for faster container startup
ENV UV_COMPILE_BYTECODE=1
# copy link mode is required when the cache and sync target are on separate filesystems
ENV UV_LINK_MODE=copy

# Install dependencies first (separate layer — only re-runs when lock/pyproject change)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy the project source
COPY . /app

# Sync again to install the project itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ============================================================
# Runtime stage — lean image without uv or build tools
# ============================================================
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy the virtual environment (third-party packages + compiled bytecode)
COPY --from=builder /app/.venv /app/.venv

# Copy the application source
COPY --from=builder /app/app /app/app

# Activate the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8123

CMD ["python", "-m", "app.main"]
