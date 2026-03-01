# =============================================================================
# Stage 1: Builder — install dependencies with uv
# =============================================================================
FROM python:3.11-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /build

# Copy dependency files first (layer cache optimization)
COPY pyproject.toml ./
COPY README.md ./

# Install dependencies into a virtual environment
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python \
        --no-cache \
        -e . 2>/dev/null || \
    uv pip install --python /opt/venv/bin/python \
        --no-cache \
        pydantic>=2.0 \
        pydantic-settings>=2.0 \
        pandas>=2.0 \
        openpyxl>=3.1 \
        rich>=13.0 \
        loguru>=0.7 \
        python-dotenv>=1.0 \
        click>=8.1 \
        "fastapi>=0.104,<1.0" \
        "uvicorn[standard]>=0.24" \
        "sqlalchemy>=2.0,<3.0" \
        alembic>=1.12 \
        "psycopg[binary]>=3.1" \
        asyncpg>=0.31.0 \
        httpx>=0.27 \
        lxml>=4.9 \
        yfinance>=0.2

# =============================================================================
# Stage 2: Runtime — lean production image
# =============================================================================
FROM python:3.11-slim AS runtime

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1001 solstein && \
    useradd --uid 1001 --gid solstein --shell /bin/bash --create-home solstein

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application source
COPY --chown=solstein:solstein src/ ./src/
COPY --chown=solstein:solstein pyproject.toml ./

# Set environment variables
ENV PYTHONPATH=/app/src \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv

# Create data directories with correct ownership
RUN mkdir -p /app/data/input /app/data/cache /app/data/output/exports /app/data/output/logs && \
    chown -R solstein:solstein /app/data

# Switch to non-root user
USER solstein

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "solstein.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
