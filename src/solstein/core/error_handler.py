"""
Error Handling Module - EPIC-011
================================

Provides comprehensive error handling, logging, and recovery mechanisms
for the Solstein application.

Stories:
- 11.1: Add logging
- 11.2: Error recovery
- 11.3: Audit logging
"""

import functools
import logging
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, TypeVar

from loguru import logger


class ErrorSeverity(Enum):
    """Error severity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ErrorRecord:
    """Record of an error for audit logging."""

    timestamp: datetime
    severity: ErrorSeverity
    component: str
    operation: str
    error_type: str
    error_message: str
    stack_trace: str | None
    context: dict[str, Any]
    recovered: bool = False
    recovery_action: str | None = None


class AuditLogger:
    """Audit logger for tracking operations and errors."""

    def __init__(self, log_dir: Path = Path("logs")):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log_path = self.log_dir / "audit.log"

        # Set up audit logger
        self._setup_audit_logger()

    def _setup_audit_logger(self) -> None:
        """Set up the audit logger."""
        audit_logger = logging.getLogger("solstein.audit")
        audit_logger.setLevel(logging.INFO)

        # File handler
        handler = logging.FileHandler(self.audit_log_path)
        handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)

        audit_logger.addHandler(handler)
        self.audit_logger = audit_logger

    def log_operation(
        self,
        component: str,
        operation: str,
        status: str,
        details: dict | None = None,
    ) -> None:
        """Log an operation for audit purposes.

        Args:
            component: Component performing the operation
            operation: Name of the operation
            status: Operation status (success, failure, etc.)
            details: Additional details
        """
        details_str = f" | Details: {details}" if details else ""
        self.audit_logger.info(f"COMPONENT={component} | OPERATION={operation} | STATUS={status}{details_str}")

    def log_error(
        self,
        error_record: ErrorRecord,
    ) -> None:
        """Log an error for audit purposes.

        Args:
            error_record: Error record to log
        """
        recovery_info = ""
        if error_record.recovered:
            recovery_info = f" | RECOVERED={error_record.recovered}"
            if error_record.recovery_action:
                recovery_info += f" | ACTION={error_record.recovery_action}"

        self.audit_logger.error(
            f"COMPONENT={error_record.component} | "
            f"OPERATION={error_record.operation} | "
            f"ERROR={error_record.error_type} | "
            f"MESSAGE={error_record.error_message}"
            f"{recovery_info}"
        )


class ErrorHandler:
    """Centralized error handler with recovery mechanisms."""

    def __init__(self):
        self.audit_logger = AuditLogger()
        self.error_history: list[ErrorRecord] = []
        self.max_history = 1000

    def handle_error(
        self,
        exception: Exception,
        component: str,
        operation: str,
        context: dict | None = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        recovery_func: Callable[[], Any] | None = None,
    ) -> tuple[bool, Any]:
        """Handle an error with optional recovery.

        Args:
            exception: The exception that occurred
            component: Component where error occurred
            operation: Operation being performed
            context: Additional context
            severity: Error severity
            recovery_func: Optional recovery function

        Returns:
            Tuple of (recovered, result)
        """
        context = context or {}

        # Create error record
        error_record = ErrorRecord(
            timestamp=datetime.now(),
            severity=severity,
            component=component,
            operation=operation,
            error_type=type(exception).__name__,
            error_message=str(exception),
            stack_trace=traceback.format_exc() if severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL] else None,
            context=context,
        )

        # Add to history
        self.error_history.append(error_record)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)

        # Log error
        self._log_error(error_record)

        # Attempt recovery
        recovered = False
        result = None
        if recovery_func:
            try:
                result = recovery_func()
                recovered = True
                error_record.recovered = True
                error_record.recovery_action = recovery_func.__name__
                logger.info(f"Recovered from error in {component}.{operation}")
            except Exception as recovery_error:
                logger.error(f"Recovery failed: {recovery_error}")

        # Log to audit
        self.audit_logger.log_error(error_record)

        return recovered, result

    def _log_error(self, error_record: ErrorRecord) -> None:
        """Log error to standard logger."""
        log_message = (
            f"[{error_record.component}.{error_record.operation}] "
            f"{error_record.error_type}: {error_record.error_message}"
        )

        if error_record.severity == ErrorSeverity.DEBUG:
            logger.debug(log_message)
        elif error_record.severity == ErrorSeverity.INFO:
            logger.info(log_message)
        elif error_record.severity == ErrorSeverity.WARNING:
            logger.warning(log_message)
        elif error_record.severity == ErrorSeverity.ERROR:
            logger.error(log_message)
        elif error_record.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)

    def get_error_summary(self) -> dict[str, Any]:
        """Get summary of recent errors.

        Returns:
            Error summary statistics
        """
        if not self.error_history:
            return {"total": 0, "by_severity": {}, "by_component": {}}

        by_severity = {}
        by_component = {}
        recovered_count = 0

        for record in self.error_history:
            # By severity
            sev = record.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1

            # By component
            comp = record.component
            by_component[comp] = by_component.get(comp, 0) + 1

            # Recovery count
            if record.recovered:
                recovered_count += 1

        return {
            "total": len(self.error_history),
            "by_severity": by_severity,
            "by_component": by_component,
            "recovered": recovered_count,
            "recovery_rate": recovered_count / len(self.error_history) if self.error_history else 0,
        }


# Global error handler instance
_error_handler: ErrorHandler | None = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


T = TypeVar("T")


def with_error_handling(
    component: str,
    operation: str,
    severity: ErrorSeverity = ErrorSeverity.ERROR,
    recovery_func: Callable[[], T] | None = None,
    default_return: T | None = None,
) -> Callable:
    """Decorator for adding error handling to functions.

    Args:
        component: Component name
        operation: Operation name
        severity: Error severity level
        recovery_func: Optional recovery function
        default_return: Default return value on error

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = get_error_handler()
                context = {"args": str(args), "kwargs": str(kwargs)}

                recovered, result = handler.handle_error(
                    exception=e,
                    component=component,
                    operation=operation,
                    context=context,
                    severity=severity,
                    recovery_func=recovery_func,
                )

                if recovered:
                    return result
                elif default_return is not None:
                    return default_return
                else:
                    raise

        return wrapper

    return decorator


def log_operation(
    component: str,
    operation: str,
) -> Callable:
    """Decorator for logging function operations.

    Args:
        component: Component name
        operation: Operation name

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            handler = get_error_handler()

            try:
                result = func(*args, **kwargs)
                handler.audit_logger.log_operation(
                    component=component,
                    operation=operation,
                    status="success",
                )
                return result
            except Exception as e:
                handler.audit_logger.log_operation(
                    component=component,
                    operation=operation,
                    status="failure",
                    details={"error": str(e)},
                )
                raise

        return wrapper

    return decorator
