# =============================================================================
# Celery Application Configuration
# =============================================================================
# This module configures the Celery application for distributed task processing.
# It sets up the broker, result backend, and task routing.
# =============================================================================

from celery import Celery

from app.config import settings


# =============================================================================
# Create Celery Application
# =============================================================================
# Use dynamic methods to get broker/backend URLs (supports REDIS_URL fallback)
celery_app = Celery(
    "brand_analytics",
    broker=settings.get_celery_broker_url(),
    backend=settings.get_celery_result_backend(),
    include=["app.tasks.analysis_tasks"],
)

# =============================================================================
# Celery Configuration
# =============================================================================
celery_app.conf.update(
    # Task Settings
    # -------------------------------------------------------------------------
    # Acknowledge tasks after they complete (not before)
    task_acks_late=True,
    # Don't lose tasks if worker crashes
    task_reject_on_worker_lost=True,
    # Retry failed tasks
    task_acks_on_failure_or_timeout=False,
    # Task time limits
    task_soft_time_limit=settings.ANALYSIS_TIMEOUT,  # 5 minutes soft limit
    task_time_limit=settings.ANALYSIS_TIMEOUT + 60,  # 6 minutes hard limit
    # Result Settings
    # -------------------------------------------------------------------------
    # Results expire after 24 hours
    result_expires=86400,
    # Serialize results as JSON
    result_serializer="json",
    # Store task state and results
    result_extended=True,
    # Serialization Settings
    # -------------------------------------------------------------------------
    # Use JSON for task messages
    task_serializer="json",
    accept_content=["json"],
    # Timezone Settings
    # -------------------------------------------------------------------------
    timezone="UTC",
    enable_utc=True,
    # Worker Settings
    # -------------------------------------------------------------------------
    # Number of tasks to prefetch per worker
    worker_prefetch_multiplier=1,
    # Concurrency (can be overridden by -c flag)
    worker_concurrency=4,
    # Logging
    worker_hijack_root_logger=False,
    # Task Routing
    # -------------------------------------------------------------------------
    # Define task queues for different priorities
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "high_priority": {
            "exchange": "high_priority",
            "routing_key": "high_priority",
        },
    },
    # Default queue
    task_default_queue="default",
    # Beat Schedule (for periodic tasks - if needed)
    # -------------------------------------------------------------------------
    # beat_schedule={
    #     "cleanup-old-analyses": {
    #         "task": "cleanup_old_analyses",
    #         "schedule": 86400.0,  # Once per day
    #     },
    # },
)


# =============================================================================
# Task State Shortcuts
# =============================================================================
# These can be imported from celery_app module
PENDING = "PENDING"
STARTED = "STARTED"
SUCCESS = "SUCCESS"
FAILURE = "FAILURE"
RETRY = "RETRY"
REVOKED = "REVOKED"
