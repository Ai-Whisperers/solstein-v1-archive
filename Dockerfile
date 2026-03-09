FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY scripts/solstein-api-server.py .
COPY scripts/agent-coordinator.py .
COPY scripts/analytics-engine.py .
COPY scripts/webhook-manager.py .
COPY scripts/ml-models-engine.py .
COPY scripts/dashboard-generator.py .
COPY scripts/integration-orchestrator.py .

RUN echo "fastapi==0.104.1" > requirements.txt && \
    echo "uvicorn==0.24.0" >> requirements.txt && \
    echo "pydantic==2.5.0" >> requirements.txt && \
    echo "PyJWT==2.8.1" >> requirements.txt && \
    echo "scikit-learn==1.3.2" >> requirements.txt && \
    echo "xgboost==2.0.3" >> requirements.txt && \
    echo "numpy==1.26.2" >> requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

ENV PYTHONUNBUFFERED=1
ENV SOLSTEIN_SECRET_KEY="${SOLSTEIN_SECRET_KEY:-solstein-dev-key}"

EXPOSE 8000

CMD ["python3", "solstein-api-server.py", "--host", "0.0.0.0", "--port", "8000"]
