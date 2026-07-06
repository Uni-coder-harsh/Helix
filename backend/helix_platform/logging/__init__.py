import contextvars
import logging
import sys
from typing import Any

import structlog

from helix_platform.config import get_settings

# Context variables for tracking request and correlation IDs across threads/tasks
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)
correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)


def contextvar_processor(
    _logger: Any, _method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Injects current request_id and correlation_id contextvars into log event."""
    req_id = request_id_var.get()
    corr_id = correlation_id_var.get()
    if req_id:
        event_dict["request_id"] = req_id
    if corr_id:
        event_dict["correlation_id"] = corr_id
    return event_dict


def configure_logging() -> None:
    """Configures structured logging using structlog and standard library routing."""
    settings = get_settings()

    # Define structlog processors pipeline
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        contextvar_processor,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Route standard logging messages through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.getLevelName(settings.LOG_LEVEL.upper()),
    )

    if settings.ENV == "prod":
        # Production uses JSON lines format for logging aggregators
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Development uses user-friendly console renderer
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.LOG_LEVEL.upper())
        ),
        cache_logger_on_first_use=True,
    )

    # Disable standard uvicorn log formatting to avoid duplication
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(logger_name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Helper factory method to get a structured logger."""
    return structlog.get_logger(name)
