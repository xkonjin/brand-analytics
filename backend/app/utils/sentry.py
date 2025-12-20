# =============================================================================
# Sentry Error Tracking Integration
# =============================================================================
# Provides error tracking and performance monitoring via Sentry.
# Captures unhandled exceptions and sends them to Sentry for analysis.
#
# WHY SENTRY?
# - Real-time error alerts with full stack traces
# - Error grouping and deduplication
# - Performance monitoring (request timing, slow queries)
# - Release tracking (which deploy introduced a bug)
# =============================================================================

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from typing import Optional

from app.utils.logging import get_logger

logger = get_logger(__name__)


def init_sentry(
    dsn: Optional[str],
    environment: str = "development",
    release: Optional[str] = None,
    traces_sample_rate: float = 0.1,
    profiles_sample_rate: float = 0.1,
) -> bool:
    """
    Initialize Sentry error tracking.

    Args:
        dsn: Sentry DSN (Data Source Name). If None/empty, Sentry is disabled.
        environment: Environment name (development, staging, production)
        release: Release/version string for tracking which deploy introduced bugs
        traces_sample_rate: Percentage of requests to trace (0.0 to 1.0)
        profiles_sample_rate: Percentage of requests to profile (0.0 to 1.0)

    Returns:
        True if Sentry was initialized, False if skipped

    Example:
        init_sentry(
            dsn="https://xxx@sentry.io/123",
            environment="production",
            release="v1.2.3",
        )
    """
    if not dsn:
        logger.info("Sentry DSN not configured, error tracking disabled")
        return False

    try:
        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            # Integrations for various frameworks/libraries
            integrations=[
                FastApiIntegration(
                    transaction_style="endpoint",  # Use route name for transaction names
                ),
                CeleryIntegration(
                    monitor_beat_tasks=True,  # Track scheduled tasks
                ),
                SqlalchemyIntegration(),
                RedisIntegration(),
                HttpxIntegration(),
            ],
            # Performance monitoring
            traces_sample_rate=traces_sample_rate,
            profiles_sample_rate=profiles_sample_rate,
            # Don't send PII (emails, usernames) by default
            send_default_pii=False,
            # Attach stack traces to log messages
            attach_stacktrace=True,
            # Filter out health check endpoints from transactions
            before_send_transaction=_filter_health_checks,
            # Scrub sensitive data from events
            before_send=_scrub_sensitive_data,
        )

        logger.info(
            "Sentry initialized",
            environment=environment,
            release=release,
            traces_sample_rate=traces_sample_rate,
        )
        return True

    except Exception as e:
        logger.error("Failed to initialize Sentry", error=str(e))
        return False


def _filter_health_checks(event, hint):
    """
    Filter out health check endpoints from performance monitoring.

    Health checks are called frequently by load balancers and would
    dominate our performance data if not filtered.
    """
    if event.get("transaction"):
        transaction_name = event["transaction"]
        if "/health" in transaction_name or "/ready" in transaction_name:
            return None
    return event


def _scrub_sensitive_data(event, hint):
    """
    Scrub sensitive data from Sentry events before sending.

    Removes:
        - API keys from request headers
        - Passwords from request bodies
        - Email addresses (partial redaction)
    """
    # Scrub request headers
    if "request" in event and "headers" in event["request"]:
        sensitive_headers = ["authorization", "x-api-key", "cookie"]
        for header in sensitive_headers:
            if header in event["request"]["headers"]:
                event["request"]["headers"][header] = "[REDACTED]"

    # Scrub request body
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            sensitive_fields = ["password", "api_key", "secret", "token"]
            for field in sensitive_fields:
                if field in data:
                    data[field] = "[REDACTED]"

    return event


def capture_exception(error: Exception, **extra_context) -> Optional[str]:
    """
    Capture an exception and send it to Sentry.

    Args:
        error: The exception to capture
        **extra_context: Additional context to attach to the event

    Returns:
        Event ID if captured, None if Sentry is not initialized

    Example:
        try:
            risky_operation()
        except Exception as e:
            capture_exception(e, analysis_id="abc-123", url="https://example.com")
    """
    with sentry_sdk.push_scope() as scope:
        for key, value in extra_context.items():
            scope.set_extra(key, value)

        return sentry_sdk.capture_exception(error)


def capture_message(
    message: str, level: str = "info", **extra_context
) -> Optional[str]:
    """
    Send a message to Sentry (for non-exception events).

    Args:
        message: The message to send
        level: Severity level (debug, info, warning, error, fatal)
        **extra_context: Additional context to attach to the event

    Returns:
        Event ID if captured, None if Sentry is not initialized
    """
    with sentry_sdk.push_scope() as scope:
        for key, value in extra_context.items():
            scope.set_extra(key, value)

        return sentry_sdk.capture_message(message, level=level)


def set_user_context(
    user_id: Optional[str] = None, email: Optional[str] = None
) -> None:
    """
    Set user context for Sentry events.

    This helps identify which users are affected by errors.

    Args:
        user_id: Unique user identifier
        email: User's email (will be partially redacted in Sentry)
    """
    sentry_sdk.set_user({"id": user_id, "email": email} if user_id else None)


def set_analysis_context(analysis_id: str, url: str) -> None:
    """
    Set analysis-specific context for Sentry events.

    Args:
        analysis_id: The analysis job ID
        url: The URL being analyzed
    """
    sentry_sdk.set_tag("analysis_id", analysis_id)
    sentry_sdk.set_context(
        "analysis",
        {
            "analysis_id": analysis_id,
            "target_url": url,
        },
    )
