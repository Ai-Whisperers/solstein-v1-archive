# =============================================================================
# Solstein Multi-Stage Dockerfile
#
# Stage 1 (builder): installs build tools, compiles C extensions, creates venv
# Stage 2 (runtime): slim image with only runtime deps + application code
#
# Used by all services (api, worker, beat) — differentiation via CMD override
# in docker-compose.yml. Do NOT create separate Dockerfiles per service.
#
# Build:  docker build -t solstein .
# Size:   Target <= 500MB (vs ~1.2GB single-stage baseline)
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: Builder
# ---------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS builder

# Build dependencies for C extensions (psycopg, lxml, bcrypt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Create virtual environment in a known location
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies first (cache layer — only rebuilds when pyproject.toml changes)
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir .

# Copy source code and install the package itself
COPY src/ ./src/
RUN pip install --no-cache-dir .

# ---------------------------------------------------------------------------
# Stage 2: Runtime
# ---------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS runtime

# Runtime-only system deps (no gcc, no build-essential, no pip cache)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 solstein && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash solstein

WORKDIR /app

# Copy virtualenv from builder (contains all installed packages)
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY src/ ./src/
ENV PYTHONPATH=/app/src

# Create data directory (writable by app for celerybeat-schedule, logs, etc.)
RUN mkdir -p /app/data && chown -R solstein:solstein /app/data

# Runtime environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER solstein

# Health check for default API service (worker/beat override in docker-compose)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

EXPOSE 8000

# Default: run the API server (exec form for proper signal handling)
CMD ["uvicorn", "solstein.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
