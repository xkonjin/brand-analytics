#!/bin/bash
# =============================================================================
# Brand Analytics API - Startup Script
# =============================================================================
# Handles database migrations, Celery worker, and API server startup.
# 
# Environment Variables:
#   PORT - Port to run the API server on (default: 8000)
#   WEB_ONLY - Set to "true" to skip Celery worker (default: false)
#   DATABASE_URL - PostgreSQL connection string (triggers migrations)
# =============================================================================

set -e

# Use PORT from environment or default to 8000
PORT="${PORT:-8000}"

echo "========================================"
echo "🚀 Brand Analytics API Startup"
echo "========================================"
echo "PORT: $PORT"
echo "WEB_ONLY: ${WEB_ONLY:-false}"
echo "DATABASE_URL: ${DATABASE_URL:+[set]}"
echo "REDIS_URL: ${REDIS_URL:+[set]}"
echo "========================================"

# Run database migrations if PostgreSQL is configured
if [[ "$DATABASE_URL" == postgresql* ]]; then
    echo "📦 Running Alembic migrations..."
    alembic upgrade head || echo "⚠️ Migration failed or already up to date"
else
    echo "⏭️ Skipping migrations (SQLite or no database)"
fi

# Start Celery worker ONLY if not in WEB_ONLY mode
if [ "$WEB_ONLY" != "true" ]; then
    echo "🔄 Starting Celery Worker in background..."
    celery -A app.tasks.celery_app.celery_app worker --loglevel=info &
    CELERY_PID=$!
    echo "   Celery PID: $CELERY_PID"
else
    echo "⏭️ WEB_ONLY mode - skipping Celery worker"
fi

# Start FastAPI server
echo "🌐 Starting API Server on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
