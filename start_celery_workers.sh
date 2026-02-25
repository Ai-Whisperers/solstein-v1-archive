#!/bin/bash
# Start Celery Workers with Debug Logging

echo "⚙️ Starting Solstein Celery Workers with Debug Mode"
echo "===================================================="

export PYTHONPATH=/home/ai-whisperers/solstein/src:$PYTHONPATH
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
