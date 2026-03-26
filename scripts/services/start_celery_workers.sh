#!/bin/bash
# Start Celery Workers with Debug Logging

echo "⚙️ Starting Solstein Celery Workers with Debug Mode"
echo "===================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
export ENVIRONMENT=development
export DEBUG=true
export LOG_LEVEL=DEBUG

# Ensure log directory exists
mkdir -p data/output/logs

# Run Celery worker with detailed logging
source .venv/bin/activate
exec celery -A solstein.worker worker \
    --loglevel=debug \
    --concurrency=4 \
    --events \
    --task-events \
    --hostname=eneve-worker@%h \
    --queues=default,scoring,export,enrichment
