# =============================================================================
# Structured Logging Configuration
# =============================================================================
# This module provides structured JSON logging with correlation IDs for
# request tracing across the application and background tasks.
#
# WHY STRUCTURED LOGGING?
# - JSON logs are machine-parseable (essential for log aggregation)
# - Correlation IDs allow tracing requests across services
# - Consistent log format makes debugging production issues easier
# - Context propagation (user, analysis_id) aids incident response
# =============================================================================

import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

import structlog
from typing import List as TypingList

# Context variable for request correlation ID
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
# Context variable for analysis ID (when processing an analysis)
analysis_id_ctx: ContextVar[Optional[str]] = ContextVar("analysis_id", default=None)


def get_correlation_id() -> str:
    """Get the current correlation ID, or generate a new one."""
    cid = correlation_id_ctx.get()
    if cid is None:
        cid = str(uuid.uuid4())
        correlation_id_ctx.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    """Set the correlation ID for the current context."""
    correlation_id_ctx.set(cid)


def set_analysis_id(analysis_id: str) -> None:
    """Set the analysis ID for the current context."""
    analysis_id_ctx.set(analysis_id)


def add_context_info(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Structlog processor that adds context information to every log entry.
    
    Adds:
        - correlation_id: Request tracing ID
        - analysis_id: Current analysis being processed (if any)
        - timestamp: ISO format timestamp
        - service: Service name for multi-service setups
    """
    event_dict["correlation_id"] = correlation_id_ctx.get()
    
    analysis_id = analysis_id_ctx.get()
    if analysis_id:
        event_dict["analysis_id"] = analysis_id
    
    event_dict["timestamp"] = datetime.utcnow().isoformat() + "Z"
    event_dict["service"] = "brand-analytics-api"
    
    return event_dict


def add_log_level(
    logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Add log level to the event dict."""
    event_dict["level"] = method_name.upper()
    return event_dict


def configure_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
    log_to_stdout: bool = True,
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, output JSON logs (production). If False, colored console logs (dev).
        log_to_stdout: If True, log to stdout. If False, logs go to stderr.
    
    Example output (JSON mode):
        {
            "event": "Analysis started",
            "correlation_id": "abc-123",
            "analysis_id": "xyz-789",
            "url": "https://example.com",
            "level": "INFO",
            "timestamp": "2025-01-15T10:30:00.000Z",
            "service": "brand-analytics-api"
        }
    """
    # Shared processors for all configurations
    shared_processors: TypingList = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        add_context_info,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    
    if json_logs:
        # Production: JSON output
        shared_processors.append(structlog.processors.format_exc_info)
        renderer = structlog.processors.JSONRenderer()
    else:
        # Development: Colored console output
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    
    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    handler = logging.StreamHandler(sys.stdout if log_to_stdout else sys.stderr)
    handler.setFormatter(logging.Formatter("%(message)s"))
    
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        A bound structlog logger
    
    Example:
        logger = get_logger(__name__)
        logger.info("Processing started", url="https://example.com", module="seo")
    """
    return structlog.get_logger(name)


# Pre-configured logger for quick imports
logger = get_logger("brand_analytics")
