# Multi-stage Docker build for Orca Agents API
FROM python:3.13-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/opt/uv-cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY .python-version ./

# Development stage
FROM base AS development

# Create virtual environment and install all dependencies (including dev)
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"
RUN --mount=type=cache,target=/opt/uv-cache \
    uv sync --frozen

# Copy application code
COPY orca_agents/ ./orca_agents/

# Create logs directory
RUN mkdir -p /app/logs

# Expose port
EXPOSE 8000

# Development command with hot reload
CMD ["uv", "run", "uvicorn", "orca_agents.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base AS production

# Create virtual environment and install production dependencies only
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"
RUN --mount=type=cache,target=/opt/uv-cache \
    uv sync --frozen --no-dev

# Copy application code
COPY orca_agents/ ./orca_agents/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash orcauser && \
    mkdir -p /app/logs /app/data && \
    chown -R orcauser:orcauser /app

# Switch to non-root user
USER orcauser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose port
EXPOSE 8000

# Production command
CMD ["uv", "run", "uvicorn", "orca_agents.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
