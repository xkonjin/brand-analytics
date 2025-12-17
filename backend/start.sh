#!/bin/bash
set -e

# Start Celery worker in background
echo "🚀 Starting Celery Worker..."
celery -A app.tasks.celery_app worker --loglevel=info &

# Start FastAPI server in foreground
echo "🚀 Starting API Server..."
uvicorn app.main:app --host 0.0.0.0 --port 8080

