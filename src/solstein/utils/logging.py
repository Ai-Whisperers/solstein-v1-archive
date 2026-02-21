import logging
import sys
from pathlib import Path
from typing import Any

from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Default handler from logging to loguru.
    See: https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-standard-library
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def format_record(record: dict[str, Any]) -> str:
    """
    Custom format for loguru records.
    Provides a clean, alchemical-themed output for development.
    """
    format_string = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    )

    # Add extra context if available (e.g., request_id, company_id)
    extra = record["extra"]
    if extra:
        context_parts = []
        for key, value in extra.items():
            context_parts.append(f"<magenta>{key}={value}</magenta>")
        format_string += f"({', '.join(context_parts)}) - "

    format_string += "<level>{message}</level>{exception}\n"
    return format_string


def setup_logging(
    level: str = "INFO",
    json_format: bool = False,
    log_file: str | Path | None = None,
    rotation: str = "500 MB",
    retention: str = "30 days",
) -> None:
    """
    Configures loguru logging with standard library interception.
    """
    # Remove all existing handlers
    logger.remove()

    # Add stdout handler
    if json_format:
        logger.add(sys.stdout, level=level, serialize=True)
    else:
        logger.add(sys.stdout, level=level, format=format_record)

    # Add file handler if requested
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        if json_format:
            logger.add(
                str(log_path),
                level=level,
                serialize=True,
                rotation=rotation,
                retention=retention,
                compression="zip",
            )
        else:
            logger.add(
                str(log_path),
                level=level,
                format=format_record,
                rotation=rotation,
                retention=retention,
                compression="zip",
            )

    # Intercept standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Intercept specific library loggers that might be chatty or important
    for logger_name in ("uvicorn", "uvicorn.access", "fastapi", "sqlalchemy"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.info(f"Aura Logging System Initialized [Level={level}, JSON={json_format}]")
