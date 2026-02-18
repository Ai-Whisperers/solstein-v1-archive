# Multi-stage Docker build for SolStein

# Stage 1: Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir .

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY examples/ ./examples/

# Stage 2: Runtime stage
FROM python:3.12-slim as runtime

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 solstein && \
    chown -R solstein:solstein /app

# Copy from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --chown=solstein:solstein . .

# Switch to non-root user
USER solstein

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["solstein", "--help"]

# Labels
LABEL org.opencontainers.image.title="SolStein"
LABEL org.opencontainers.image.description="AI-Powered Competitive Intelligence Platform"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.authors="AI Whisperers"
LABEL org.opencontainers.image.url="https://github.com/Ai-Whisperers/solstein"
LABEL org.opencontainers.image.source="https://github.com/Ai-Whisperers/solstein"
LABEL org.opencontainers.image.licenses="Proprietary"