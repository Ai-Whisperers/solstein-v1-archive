#!/bin/bash
# scripts/stop-dev.sh
# Stop the Solstein development environment

set -e

echo "🛑 Stopping Solstein development environment..."

# Stop API server
if [ -f .pid.api ]; then
    PID=$(cat .pid.api)
    if ps -p $PID > /dev/null 2>&1; then
        echo "🌐 Stopping API server (PID: $PID)..."
        kill $PID 2>/dev/null || true
        sleep 2
        if ps -p $PID > /dev/null 2>&1; then
            echo "   Force killing API server..."
            kill -9 $PID 2>/dev/null || true
        fi
        echo "   ✅ API server stopped"
    fi
    rm -f .pid.api
else
    echo "   ℹ️  API server not running"
fi

# Stop Celery worker
if [ -f .pid.worker ]; then
    PID=$(cat .pid.worker)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚙️  Stopping Celery worker (PID: $PID)..."
        kill $PID 2>/dev/null || true
        sleep 2
        if ps -p $PID > /dev/null 2>&1; then
            echo "   Force killing Celery worker..."
            kill -9 $PID 2>/dev/null || true
        fi
        echo "   ✅ Celery worker stopped"
    fi
    rm -f .pid.worker
else
    echo "   ℹ️  Celery worker not running"
fi

echo ""
echo "✅ Solstein dev environment stopped"
echo "   To restart: ./scripts/start-dev.sh"
