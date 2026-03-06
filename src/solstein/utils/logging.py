"""Logging configuration with unified Loguru pipeline and context integration."""

import logging
import sys
from pathlib import Path
from typing import Any

from loguru import logger

from .context import get_current_context


class InterceptHandler(logging.Handler):
    """Intercept stdlib logging and route to Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller frame (skip logging internals)
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def format_record(record: dict[str, Any]) -> str:
    """Format log record with automatic context inclusion."""
    format_string = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
    )

    # Auto-include contextvars context
    context = get_current_context()
    if context:
        context_str = " | ".join(f"<magenta>{k}</magenta>=<yellow>{v}</yellow>" for k, v in context.items())
        format_string += " | " + context_str

    # Add any explicit extra fields (excluding context keys to avoid duplication)
    extra = record.get("extra", {})
    extra_fields = {k: v for k, v in extra.items() if k not in context and k not in ("correlation_id", "request_id")}
    if extra_fields:
        extra_str = " | ".join(f"<magenta>{k}</magenta>=<yellow>{v}</yellow>" for k, v in extra_fields.items())
        format_string += " | " + extra_str

    format_string += " - <level>{message}</level>\n{exception}"
    return format_string


def format_record_json(record: dict[str, Any]) -> dict[str, Any]:
    """Format record for JSON output with context."""
    # Start with standard fields
    output = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "source": {
            "file": record["file"].path,
            "function": record["function"],
            "line": record["line"],
        },
    }

    # Add automatic context
    context = get_current_context()
    if context:
        output["context"] = context

    # Add extra fields
    extra = record.get("extra", {})
    if extra:
        output["extra"] = {k: v for k, v in extra.items() if k not in context}

    # Add exception info
    if record["exception"]:
        output["exception"] = {
            "type": record["exception"].type.__name__ if record["exception"].type else None,
            "value": str(record["exception"].value) if record["exception"].value else None,
            "traceback": record["exception"].traceback,
        }

    return output


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: str | Path | None = None,
    rotation: str = "500 MB",
    retention: str = "30 days",
) -> None:
    """Configure unified logging with Loguru.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON formatting for production
        log_file: Optional file path for logging
        rotation: Log rotation size
        retention: Log retention period
    """
    # Remove default handler
    logger.remove()

    # Add stdout handler
    if json_format:
        logger.add(
            sys.stdout,
            level=level,
            serialize=True,
            format="{message}",  # JSON serialization handles format
        )
    else:
        logger.add(
            sys.stdout,
            level=level,
            format=format_record,
            colorize=True,
        )

    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.add(
            str(log_path),
            level=level,
            rotation=rotation,
            retention=retention,
            compression="gz",
            serialize=json_format,
            format="{message}" if json_format else format_record,
        )

    # Intercept stdlib logging - CRITICAL for unified pipeline
    logging.basicConfig(
        handlers=[InterceptHandler()],
        level=logging.NOTSET,  # Let Loguru handle filtering
        force=True,
    )

    # Configure third-party loggers to use our handler
    for log_name in ("uvicorn", "uvicorn.access", "fastapi", "sqlalchemy"):
        logging_logger = logging.getLogger(log_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.info(
        "Logging system initialized",
        level=level,
        json_format=json_format,
        log_file=str(log_file) if log_file else None,
    )
