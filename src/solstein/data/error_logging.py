"""
Phase 2.C: Error Logging & Visibility Module

Standardized logging, error alerting integration, and error metrics collection.
"""

import logging
from collections.abc import Callable
from datetime import datetime, timezone
from enum import Enum


class LogLevel(str, Enum):
    """Standardized log levels."""

    DEBUG = "DEBUG"  # Technical details, verbose
    INFO = "INFO"  # Business events, important milestones
    WARNING = "WARNING"  # Unexpected but recoverable
    ERROR = "ERROR"  # Error occurred, operation failed
    CRITICAL = "CRITICAL"  # System failure, immediate action needed


class ErrorType(str, Enum):
    """Error type classification."""

    NO_DATA_FOUND = "NO_DATA_FOUND"  # API returned no data (not an error)
    API_ERROR = "API_ERROR"  # API call failed
    DATA_ERROR = "DATA_ERROR"  # Data validation failed
    VALIDATION_ERROR = "VALIDATION_ERROR"  # Input validation failed
    NETWORK_ERROR = "NETWORK_ERROR"  # Network/connectivity issue
    TIMEOUT_ERROR = "TIMEOUT_ERROR"  # Request timed out
    UNKNOWN = "UNKNOWN"  # Unknown error type


class ErrorLogger:
    """Centralized error logging with standardized levels and alerting."""

    def __init__(self, logger: logging.Logger, alert_callback: Callable | None = None):
        """Initialize error logger.

        Args:
            logger: Python logger instance
            alert_callback: Optional callback for alerting (e.g., Sentry, DataDog)
        """
        self.logger = logger
        self.alert_callback = alert_callback
        self.error_count = 0
        self.error_by_type = {}

    def log_no_data_found(self, context: str, source: str) -> None:
        """Log when API returns no data (not an error).

        Item 49: Differentiate "no data found" from errors
        """
        msg = f"No data found from {source} for {context}"
        self.logger.info(msg)  # INFO level, not WARNING

    def log_api_error(self, context: str, source: str, error: Exception, attempt: int = 1) -> None:
        """Log API error with context.

        Item 43: Error messages lack context
        Item 52: Standardize logger levels
        """
        msg = f"API error from {source} for {context} (attempt {attempt}): {str(error)}"
        self.logger.warning(msg)
        self._track_error(ErrorType.API_ERROR)
        self._maybe_alert(msg, LogLevel.WARNING)

    def log_data_validation_error(self, context: str, field: str, error: str) -> None:
        """Log data validation error.

        Item 52: Standardize logger levels
        """
        msg = f"Data validation failed for {context}.{field}: {error}"
        self.logger.warning(msg)
        self._track_error(ErrorType.DATA_ERROR)

    def log_enrichment_step(self, company_name: str, step: str, status: str) -> None:
        """Log enrichment step progress.

        Item 58: Error context lost between enrichment calls
        """
        msg = f"Enrichment step '{step}' for {company_name}: {status}"
        self.logger.debug(msg)  # DEBUG level for technical details

    def log_enrichment_complete(self, company_name: str, sources: list[str], error_count: int) -> None:
        """Log enrichment completion.

        Item 52: Standardize logger levels
        """
        if error_count == 0:
            msg = f"Enrichment complete for {company_name} from {sources}"
            self.logger.info(msg)
        else:
            msg = f"Enrichment complete for {company_name} with {error_count} errors"
            self.logger.warning(msg)
            self._maybe_alert(msg, LogLevel.WARNING)

    def log_critical_error(self, context: str, error: Exception) -> None:
        """Log critical error requiring immediate attention.

        Item 42: Add error severity levels
        """
        msg = f"CRITICAL ERROR in {context}: {str(error)}"
        self.logger.critical(msg)
        self._track_error(ErrorType.UNKNOWN)
        self._maybe_alert(msg, LogLevel.CRITICAL)

    def log_timeout_error(self, context: str, timeout_seconds: int) -> None:
        """Log timeout error.

        Item 52: Standardize logger levels
        """
        msg = f"Timeout after {timeout_seconds}s for {context}"
        self.logger.error(msg)
        self._track_error(ErrorType.TIMEOUT_ERROR)
        self._maybe_alert(msg, LogLevel.ERROR)

    def log_network_error(self, context: str, error: Exception) -> None:
        """Log network error.

        Item 52: Standardize logger levels
        """
        msg = f"Network error for {context}: {str(error)}"
        self.logger.error(msg)
        self._track_error(ErrorType.NETWORK_ERROR)
        self._maybe_alert(msg, LogLevel.ERROR)

    def _track_error(self, error_type: ErrorType) -> None:
        """Track error count by type.

        Item 48: Add error metrics/counters
        """
        self.error_count += 1
        if error_type not in self.error_by_type:
            self.error_by_type[error_type] = 0
        self.error_by_type[error_type] += 1

    def _maybe_alert(self, message: str, level: LogLevel) -> None:
        """Send alert if callback configured.

        Item 55: Add error alerting mechanism
        """
        if self.alert_callback and level in [LogLevel.ERROR, LogLevel.CRITICAL]:
            try:
                self.alert_callback(message, level)
            except Exception as e:
                self.logger.error(f"Failed to send alert: {e}")

    def get_error_summary(self) -> dict:
        """Get error summary for reporting.

        Item 61: Create error summary reports
        """
        return {
            "total_errors": self.error_count,
            "errors_by_type": dict(self.error_by_type),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def reset_counters(self) -> None:
        """Reset error counters."""
        self.error_count = 0
        self.error_by_type = {}


class ErrorSampler:
    """Sample errors for high-volume scenarios.

    Item 57: Implement error sampling for high-volume scenarios
    """

    def __init__(self, sample_rate: float = 0.1):
        """Initialize error sampler.

        Args:
            sample_rate: Fraction of errors to log (0.0-1.0)
        """
        self.sample_rate = sample_rate
        self.error_count = 0

    def should_log(self) -> bool:
        """Determine if error should be logged."""
        self.error_count += 1
        # Log first error, then sample
        if self.error_count == 1:
            return True
        if self.sample_rate <= 0:
            return False
        return (self.error_count % max(1, int(1 / self.sample_rate))) == 0


class ErrorCorrelationTracker:
    """Track related errors across calls.

    Item 59: Add error correlation IDs
    """

    def __init__(self):
        """Initialize correlation tracker."""
        self.correlation_id = None
        self.related_errors = []

    def start_correlation(self, correlation_id: str) -> None:
        """Start tracking related errors."""
        self.correlation_id = correlation_id
        self.related_errors = []

    def add_error(self, error_msg: str) -> None:
        """Add error to correlation."""
        if self.correlation_id:
            self.related_errors.append(
                {
                    "correlation_id": self.correlation_id,
                    "error": error_msg,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

    def get_correlated_errors(self) -> list[dict]:
        """Get all errors in current correlation."""
        return self.related_errors

    def end_correlation(self) -> None:
        """End correlation tracking."""
        self.correlation_id = None
        self.related_errors = []


class ErrorMetricsCollector:
    """Collect error metrics for dashboards.

    Item 56: Implement error metrics collection
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            "total_errors": 0,
            "errors_by_source": {},
            "errors_by_type": {},
            "errors_by_hour": {},
            "last_error_time": None,
        }

    def record_error(self, source: str, error_type: str) -> None:
        """Record error for metrics."""
        self.metrics["total_errors"] += 1

        # Track by source
        if source not in self.metrics["errors_by_source"]:
            self.metrics["errors_by_source"][source] = 0
        self.metrics["errors_by_source"][source] += 1

        # Track by type
        if error_type not in self.metrics["errors_by_type"]:
            self.metrics["errors_by_type"][error_type] = 0
        self.metrics["errors_by_type"][error_type] += 1

        # Track by hour
        now = datetime.now(timezone.utc)
        hour_key = now.strftime("%Y-%m-%d %H:00")
        if hour_key not in self.metrics["errors_by_hour"]:
            self.metrics["errors_by_hour"][hour_key] = 0
        self.metrics["errors_by_hour"][hour_key] += 1

        # Update last error time
        self.metrics["last_error_time"] = now.isoformat()

    def get_metrics(self) -> dict:
        """Get current metrics."""
        return self.metrics

    def reset_metrics(self) -> None:
        """Reset metrics."""
        self.metrics = {
            "total_errors": 0,
            "errors_by_source": {},
            "errors_by_type": {},
            "errors_by_hour": {},
            "last_error_time": None,
        }
