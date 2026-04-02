"""Shared logging configuration with zero application-layer imports.

STORY-117: Provides structured logging setup used across all layers.
"""

from __future__ import annotations

import logging
import sys


def configure_logging(
    level: str = "INFO",
    *,
    json_format: bool = False,
    module_name: str | None = None,
) -> logging.Logger:
    """Configure and return a logger with standard Solstein formatting.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        json_format: If True, use JSON-structured log output.
        module_name: Logger name. Defaults to root logger.

    Returns:
        Configured logger instance.
    """
    logger_name = module_name or "solstein"
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        if json_format:
            fmt = '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        else:
            fmt = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger following Solstein conventions.

    This is a thin wrapper for consistency. Use instead of
    ``logging.getLogger(__name__)``.
    """
    return logging.getLogger(name)
