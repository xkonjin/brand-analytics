# =============================================================================
# Celery Worker Entry Point
# =============================================================================
# This script starts the Celery worker for processing analysis tasks.
#
# Usage:
#   celery -A celery_worker worker --loglevel=info
#
# Or with concurrency:
#   celery -A celery_worker worker --loglevel=info --concurrency=4
# =============================================================================

from app.tasks.celery_app import celery_app

# Import tasks to register them with Celery

if __name__ == "__main__":
    celery_app.start()
