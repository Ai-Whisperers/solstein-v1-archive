#!/bin/bash
# Start Solstein API Server with Debug Logging

echo "🌐 Starting Solstein FastAPI Server with Debug Mode"
echo "===================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
export ENVIRONMENT=development
export DEBUG=true
export LOG_LEVEL=DEBUG

# Ensure log directory exists
mkdir -p data/output/logs

# Run with uvicorn with reload and detailed logging
source .venv/bin/activate
exec uvicorn solstein.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level debug \
    --access-log \
    --use-colors \
    --proxy-headers
