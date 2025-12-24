"""
Structured logging configuration for Quoted.

INFRA-008: Centralized logging with structured format for production observability.
Replaces print() statements with proper logging levels and searchable fields.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Optional, Dict, Any


class StructuredFormatter(logging.Formatter):
    """
    JSON-structured log formatter for production.
    Outputs logs in a format easily parsed by Railway/Datadog/etc.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        # Add common context fields
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        if hasattr(record, "contractor_id"):
            log_entry["contractor_id"] = record.contractor_id
        if hasattr(record, "quote_id"):
            log_entry["quote_id"] = record.quote_id
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        return json.dumps(log_entry)


class DevelopmentFormatter(logging.Formatter):
    """
    Human-readable formatter for development.
    Colored output with clear structure.
    """

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Truncate long logger names
        logger_name = record.name
        if len(logger_name) > 20:
            logger_name = "..." + logger_name[-17:]

        base = f"{color}[{timestamp}] {record.levelname:8}{self.RESET} {logger_name:20} | {record.getMessage()}"

        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"

        return base


def configure_logging(
    environment: str = "development",
    log_level: str = "INFO"
) -> None:
    """
    Configure application-wide logging.

    Args:
        environment: "development" or "production"
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers = []

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level.upper()))

    # Use appropriate formatter based on environment
    if environment == "production":
        handler.setFormatter(StructuredFormatter())
    else:
        handler.setFormatter(DevelopmentFormatter())

    root_logger.addHandler(handler)

    # Silence noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.

    Usage:
        logger = get_logger(__name__)
        logger.info("User logged in", extra={"user_id": user_id})
        logger.error("Failed to process", exc_info=True)
    """
    return logging.getLogger(name)


class LogContext:
    """
    Context manager for adding extra fields to logs.

    Usage:
        with LogContext(user_id="123", request_id="abc"):
            logger.info("Processing request")  # Includes user_id and request_id
    """

    _context: Dict[str, Any] = {}

    def __init__(self, **kwargs):
        self.fields = kwargs
        self._previous = {}

    def __enter__(self):
        self._previous = LogContext._context.copy()
        LogContext._context.update(self.fields)
        return self

    def __exit__(self, *args):
        LogContext._context = self._previous

    @classmethod
    def get_context(cls) -> Dict[str, Any]:
        return cls._context.copy()


# Pre-configured loggers for common modules
def get_auth_logger() -> logging.Logger:
    """Logger for authentication events."""
    return get_logger("quoted.auth")


def get_billing_logger() -> logging.Logger:
    """Logger for billing/subscription events."""
    return get_logger("quoted.billing")


def get_email_logger() -> logging.Logger:
    """Logger for email sending."""
    return get_logger("quoted.email")


def get_quote_logger() -> logging.Logger:
    """Logger for quote generation."""
    return get_logger("quoted.quote")


def get_api_logger() -> logging.Logger:
    """Logger for API endpoints."""
    return get_logger("quoted.api")


def get_db_logger() -> logging.Logger:
    """Logger for database operations."""
    return get_logger("quoted.db")


def get_migration_logger() -> logging.Logger:
    """Logger for database migrations."""
    return get_logger("quoted.migration")
