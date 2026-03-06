"""Dependency tracing and metrics collection.

This module provides tracing for outbound dependency calls (database, LLM, HTTP)
with timing, correlation ID propagation, and failure tracking.
"""

import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from dataclasses import dataclass, field
from collections import defaultdict
from statistics import median
from loguru import logger
from .context import get_current_context


@dataclass
class DependencyCall:
    """Record of a dependency call."""

    service: str  # 'postgresql', 'openai', 'crunchbase', etc.
    operation: str  # 'query', 'generate', 'get_company', etc.
    duration_ms: float
    success: bool
    error_type: str | None = None
    metadata: dict = field(default_factory=dict)


class DependencyTracer:
    """Trace and collect metrics for dependency calls."""

    def __init__(self):
        self._calls: list[DependencyCall] = []
        self._max_calls = 10000  # Prevent unbounded growth

    @asynccontextmanager
    async def trace(
        self,
        service: str,
        operation: str,
        **metadata: Any,
    ) -> AsyncGenerator[dict, None]:
        """Context manager for tracing a dependency call.

        Usage:
            async with tracer.trace("openai", "generate", model="gpt-4") as span:
                span["request_tokens"] = 100  # Add metadata during call
                response = await openai.generate(prompt)
                span["response_tokens"] = 50
        """
        start = time.perf_counter()
        span_metadata = dict(metadata)
        error = None

        # Get correlation context
        context = get_current_context()

        logger.debug(
            f"Dependency call started: {service}.{operation}",
            service=service,
            operation=operation,
            **context,
            **metadata,
        )

        try:
            yield span_metadata
            success = True
        except Exception as e:
            success = False
            error = e
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000

            call = DependencyCall(
                service=service,
                operation=operation,
                duration_ms=duration_ms,
                success=success,
                error_type=type(error).__name__ if error else None,
                metadata=span_metadata,
            )

            self._record_call(call)

            log_level = "error" if not success else ("warning" if duration_ms > 1000 else "debug")
            logger.log(
                log_level,
                f"Dependency call completed: {service}.{operation}",
                service=service,
                operation=operation,
                duration_ms=round(duration_ms, 2),
                success=success,
                error_type=call.error_type,
                **context,
                **span_metadata,
            )

    def _record_call(self, call: DependencyCall) -> None:
        """Record call, maintaining size limit."""
        if len(self._calls) >= self._max_calls:
            self._calls = self._calls[len(self._calls) // 2 :]  # Drop oldest half
        self._calls.append(call)

    def get_metrics(self, service: str | None = None) -> dict[str, Any]:
        """Get aggregated metrics for dependencies.

        Returns:
            Dictionary with p50, p95, p99 latencies and error rates per service.
        """
        calls = self._calls
        if service:
            calls = [c for c in calls if c.service == service]

        if not calls:
            return {}

        # Group by service
        by_service = defaultdict(list)
        for call in calls:
            by_service[call.service].append(call)

        metrics = {}
        for svc, svc_calls in by_service.items():
            durations = [c.duration_ms for c in svc_calls]
            errors = sum(1 for c in svc_calls if not c.success)

            metrics[svc] = {
                "total_calls": len(svc_calls),
                "error_count": errors,
                "error_rate": errors / len(svc_calls),
                "latency_ms": {
                    "p50": median(durations),
                    "p95": self._percentile(durations, 95),
                    "p99": self._percentile(durations, 99),
                    "avg": sum(durations) / len(durations),
                    "max": max(durations),
                },
            }

        return metrics

    def _percentile(self, data: list[float], percentile: int) -> float:
        """Calculate percentile of data."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


# Global tracer instance
tracer = DependencyTracer()


def get_tracer() -> DependencyTracer:
    """Get the global dependency tracer."""
    return tracer
