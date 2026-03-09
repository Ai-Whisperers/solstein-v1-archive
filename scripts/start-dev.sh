#!/bin/bash
# scripts/start-dev.sh
# Start the full Solstein development environment

set -e

echo "🚀 Starting Solstein development environment..."

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL not running on localhost:5432"
    echo "   Start with: docker-compose up -d postgres"
    exit 1
fi
echo "✅ PostgreSQL is running"

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis not running on localhost:6379"
    echo "   Start with: docker-compose up -d redis"
    exit 1
fi
echo "✅ Redis is running"

if ! .venv/bin/python3 -c "import redis" > /dev/null 2>&1; then
    echo "❌ Python module 'redis' not installed in .venv"
    echo "   Install with: .venv/bin/pip install redis"
    exit 1
fi
echo "✅ Python redis module is available"

# Create logs directory
mkdir -p logs

# Set PYTHONPATH
export PYTHONPATH=src

# Check if API is already running
if [ -f .pid.api ]; then
    PID=$(cat .pid.api)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  API server already running (PID: $PID)"
        echo "   Stop with: ./scripts/stop-dev.sh"
    else
        rm .pid.api
    fi
fi

# Check if Worker is already running
if [ -f .pid.worker ]; then
    PID=$(cat .pid.worker)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Celery worker already running (PID: $PID)"
        echo "   Stop with: ./scripts/stop-dev.sh"
    else
        rm .pid.worker
    fi
fi

# Start API server
echo "🌐 Starting API server..."
.venv/bin/python3 -m uvicorn solstein.api.main:app --reload --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
echo $! > .pid.api
echo "   PID: $(cat .pid.api) | Logs: logs/api.log"

# Start Celery worker
echo "⚙️  Starting Celery worker..."
.venv/bin/celery -A solstein.celery_config worker --loglevel=info > logs/worker.log 2>&1 &
echo $! > .pid.worker
echo "   PID: $(cat .pid.worker) | Logs: logs/worker.log"

# Wait for API to be ready
echo "⏳ Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is ready!"
        break
    fi
    sleep 1
done

echo ""
echo "🎉 Solstein dev environment is running!"
echo ""
echo "   API:        http://localhost:8000"
echo "   Docs:       http://localhost:8000/docs"
echo "   Health:     http://localhost:8000/health"
echo "   API Logs:   tail -f logs/api.log"
echo "   Worker Logs: tail -f logs/worker.log"
echo ""
echo "   Stop with: ./scripts/stop-dev.sh"
