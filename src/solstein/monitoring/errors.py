"""Error tracking and analysis.

EPIC-026 Story 6: Implements comprehensive error tracking including:
- Error classification
- Error trend analysis
- Sentry integration support
- Error aggregation by endpoint/category

Usage:
    from solstein.monitoring.errors import ErrorTracker, ErrorCategory

    tracker = ErrorTracker()
    tracker.track_error(exception, context={"endpoint": "/api/companies"})
"""

import hashlib
import traceback
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from loguru import logger


class ErrorCategory(Enum):
    """Error classification categories."""

    DATABASE = "database"
    LLM_PROVIDER = "llm_provider"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    RATE_LIMIT = "rate_limit"
    NETWORK = "network"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class ErrorRecord:
    """Record of a single error occurrence."""

    category: ErrorCategory
    error_type: str
    message: str
    stack_trace: str
    timestamp: float
    fingerprint: str
    context: dict[str, Any] = field(default_factory=dict)
    count: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "error_type": self.error_type,
            "message": self.message,
            "fingerprint": self.fingerprint,
            "timestamp": self.timestamp,
            "context": self.context,
            "count": self.count,
        }


@dataclass
class ErrorTrend:
    """Error trend over time."""

    fingerprint: str
    category: ErrorCategory
    error_type: str
    message: str
    first_seen: float
    last_seen: float
    total_count: int
    trend: str  # increasing, decreasing, stable


class ErrorClassifier:
    """Classify errors by type and category."""

    def classify(self, error: Exception) -> ErrorCategory:
        """Classify an error.

        Args:
            error: Exception to classify.

        Returns:
            Error category.
        """
        error_type = type(error).__name__.lower()
        error_msg = str(error).lower()

        # Database errors
        if any(k in error_type for k in ["database", "sql", "db", "postgres"]):
            return ErrorCategory.DATABASE

        # LLM errors
        if any(k in error_type for k in ["llm", "openai", "anthropic", "groq"]):
            return ErrorCategory.LLM_PROVIDER

        # Validation errors
        if any(k in error_type for k in ["validation", "invalid", "valueerror"]):
            return ErrorCategory.VALIDATION

        # Auth errors
        if any(k in error_type for k in ["authentication", "unauthenticated", "401"]):
            return ErrorCategory.AUTHENTICATION

        # Authorization errors
        if any(k in error_type for k in ["authorization", "forbidden", "403"]):
            return ErrorCategory.AUTHORIZATION

        # Rate limit
        if any(k in error_msg for k in ["rate limit", "too many requests", "429"]):
            return ErrorCategory.RATE_LIMIT

        # Network errors
        if any(k in error_type for k in ["connection", "network", "timeout", "aiohttp"]):
            if "timeout" in error_msg:
                return ErrorCategory.TIMEOUT
            return ErrorCategory.NETWORK

        return ErrorCategory.UNKNOWN


class ErrorTracker:
    """Track and analyze errors."""

    def __init__(self, max_history: int = 5000):
        """Initialize error tracker.

        Args:
            max_history: Maximum error records to keep.
        """
        self.max_history = max_history
        self.errors: list[ErrorRecord] = []
        self.classifier = ErrorClassifier()
        self.error_counts: dict[str, int] = defaultdict(int)

    def _generate_fingerprint(self, error: Exception) -> str:
        """Generate error fingerprint for deduplication.

        Args:
            error: Exception to fingerprint.

        Returns:
            Fingerprint hash.
        """
        # Use error type and first line of stack trace
        tb = traceback.format_exc().split("\n")[:3]
        content = f"{type(error).__name__}:{str(error)[:100]}:{':'.join(tb)}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def track_error(
        self,
        error: Exception,
        context: dict[str, Any] | None = None,
    ) -> ErrorRecord:
        """Track an error occurrence.

        Args:
            error: Exception that occurred.
            context: Additional context (endpoint, user_id, etc.).

        Returns:
            ErrorRecord.
        """
        import time

        category = self.classifier.classify(error)
        fingerprint = self._generate_fingerprint(error)
        tb = traceback.format_exc()

        record = ErrorRecord(
            category=category,
            error_type=type(error).__name__,
            message=str(error),
            stack_trace=tb,
            timestamp=time.time(),
            fingerprint=fingerprint,
            context=context or {},
        )

        # Check for duplicate
        existing = self._find_by_fingerprint(fingerprint)
        if existing:
            existing.count += 1
            existing.last_seen = record.timestamp
            record = existing
        else:
            self.errors.append(record)

        self.error_counts[fingerprint] = record.count

        # Trim history
        if len(self.errors) > self.max_history:
            self.errors = self.errors[-self.max_history :]

        # Log
        logger.error(
            f"Error tracked [{category.value}]: {error}",
            fingerprint=fingerprint,
            context=context,
        )

        return record

    def _find_by_fingerprint(self, fingerprint: str) -> ErrorRecord | None:
        """Find error by fingerprint.

        Args:
            fingerprint: Error fingerprint.

        Returns:
            ErrorRecord if found.
        """
        for error in self.errors:
            if error.fingerprint == fingerprint:
                return error
        return None

    def get_errors_by_category(
        self,
        category: ErrorCategory,
        since: float | None = None,
    ) -> list[ErrorRecord]:
        """Get errors filtered by category.

        Args:
            category: Error category.
            since: Unix timestamp filter.

        Returns:
            List of matching errors.
        """
        errors = [e for e in self.errors if e.category == category]
        if since:
            errors = [e for e in errors if e.timestamp >= since]
        return errors

    def get_errors_by_endpoint(self, endpoint: str) -> list[ErrorRecord]:
        """Get errors for a specific endpoint.

        Args:
            endpoint: Endpoint path.

        Returns:
            List of matching errors.
        """
        return [e for e in self.errors if e.context.get("endpoint") == endpoint]

    def get_top_errors(self, n: int = 10) -> list[ErrorRecord]:
        """Get most frequent errors.

        Args:
            n: Number of errors to return.

        Returns:
            List of errors sorted by frequency.
        """
        return sorted(self.errors, key=lambda e: e.count, reverse=True)[:n]

    def analyze_trends(self, window_hours: int = 24) -> list[ErrorTrend]:
        """Analyze error trends.

        Args:
            window_hours: Analysis window in hours.

        Returns:
            List of error trends.
        """
        import time

        cutoff = time.time() - (window_hours * 3600)
        recent_errors = [e for e in self.errors if e.timestamp >= cutoff]

        # Group by fingerprint
        by_fingerprint: dict[str, list[ErrorRecord]] = defaultdict(list)
        for e in recent_errors:
            by_fingerprint[e.fingerprint].append(e)

        trends = []
        for fingerprint, occurrences in by_fingerprint.items():
            if len(occurrences) < 2:
                continue

            # Sort by time
            occurrences.sort(key=lambda e: e.timestamp)

            first = occurrences[0]
            last = occurrences[-1]

            # Calculate trend
            first_half = occurrences[: len(occurrences) // 2]
            second_half = occurrences[len(occurrences) // 2 :]

            first_rate = len(first_half) / max(1, window_hours / 2)
            second_rate = len(second_half) / max(1, window_hours / 2)

            if second_rate > first_rate * 1.5:
                trend = "increasing"
            elif second_rate < first_rate * 0.5:
                trend = "decreasing"
            else:
                trend = "stable"

            trends.append(
                ErrorTrend(
                    fingerprint=fingerprint,
                    category=first.category,
                    error_type=first.error_type,
                    message=first.message,
                    first_seen=first.timestamp,
                    last_seen=last.timestamp,
                    total_count=sum(e.count for e in occurrences),
                    trend=trend,
                )
            )

        return sorted(trends, key=lambda t: t.total_count, reverse=True)

    def get_summary(self) -> dict[str, Any]:
        """Get error summary statistics.

        Returns:
            Summary dictionary.
        """
        import time

        total = len(self.errors)
        by_category = defaultdict(int)
        for e in self.errors:
            by_category[e.category.value] += e.count

        # Recent (last hour)
        hour_ago = time.time() - 3600
        recent_count = sum(e.count for e in self.errors if e.timestamp >= hour_ago)

        return {
            "total_unique_errors": total,
            "total_occurrences": sum(e.count for e in self.errors),
            "by_category": dict(by_category),
            "recent_1h": recent_count,
            "top_errors": [
                {"type": e.error_type, "message": e.message[:100], "count": e.count} for e in self.get_top_errors(5)
            ],
        }


class SentryIntegration:
    """Sentry error tracking integration."""

    @staticmethod
    def init(sentry_dsn: str | None = None, environment: str = "production"):
        """Initialize Sentry integration.

        Args:
            sentry_dsn: Sentry DSN.
            environment: Deployment environment.
        """
        if not sentry_dsn:
            logger.warning("Sentry DSN not configured")
            return

        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration

            sentry_sdk.init(
                dsn=sentry_dsn,
                environment=environment,
                integrations=[
                    FastApiIntegration(),
                ],
                traces_sample_rate=0.1,
                profiles_sample_rate=0.1,
            )
            logger.info("Sentry initialized")
        except ImportError:
            logger.warning("sentry-sdk not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Sentry: {e}")

    @staticmethod
    def capture_exception(error: Exception, context: dict[str, Any] | None = None):
        """Capture exception in Sentry.

        Args:
            error: Exception to capture.
            context: Additional context.
        """
        try:
            import sentry_sdk

            with sentry_sdk.push_scope() as scope:
                if context:
                    for key, value in context.items():
                        scope.set_extra(key, value)
                sentry_sdk.capture_exception(error)
        except ImportError:
            pass
        except Exception as e:
            logger.error(f"Failed to capture exception in Sentry: {e}")


# Global error tracker instance
global_error_tracker = ErrorTracker()
