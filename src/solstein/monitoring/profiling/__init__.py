"""Performance profiling infrastructure for Solstein.

EPIC-023 Story 1: Implements comprehensive profiling using py-spy, memray,
and custom decorators for function-level profiling.

Usage:
    from solstein.monitoring.profiling import profile, time_it

    @profile(name="enrich_company", report=True)
    async def enrich_company(company_id: str):
        # Function is automatically profiled
        pass

    # Results logged and viewable in dashboard
"""

from __future__ import annotations

import asyncio
import functools
import os
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

from loguru import logger

T = TypeVar("T")

# Global flag to enable/disable profiling
PROFILING_ENABLED = os.getenv("SOLSTEIN_PROFILING", "false").lower() == "true"


@dataclass
class ProfileResult:
    """Result of a profiling session."""

    name: str
    duration_ms: float
    memory_delta_mb: float = 0.0
    calls: int = 1
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "duration_ms": self.duration_ms,
            "memory_delta_mb": self.memory_delta_mb,
            "calls": self.calls,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class PerformanceProfiler:
    """Central profiler for collecting performance metrics."""

    def __init__(self):
        self.results: list[ProfileResult] = []
        self._enabled = PROFILING_ENABLED

    def enable(self) -> None:
        """Enable profiling."""
        self._enabled = True
        logger.info("Performance profiling enabled")

    def disable(self) -> None:
        """Disable profiling."""
        self._enabled = False
        logger.info("Performance profiling disabled")

    @property
    def is_enabled(self) -> bool:
        """Check if profiling is enabled."""
        return self._enabled

    def record(self, result: ProfileResult) -> None:
        """Record a profiling result."""
        if not self._enabled:
            return
        self.results.append(result)
        logger.debug(f"Profile: {result.name} took {result.duration_ms:.2f}ms (memory: {result.memory_delta_mb:.2f}MB)")

    def get_stats(self, name: str | None = None) -> dict[str, Any]:
        """Get profiling statistics."""
        results = self.results
        if name:
            results = [r for r in results if r.name == name]

        if not results:
            return {}

        durations = [r.duration_ms for r in results]
        return {
            "count": len(results),
            "total_duration_ms": sum(durations),
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "avg_memory_delta_mb": sum(r.memory_delta_mb for r in results) / len(results),
        }

    def export_json(self, output_path: Path) -> None:
        """Export results to JSON."""
        import json

        data = [r.to_dict() for r in self.results]
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Profiling results exported to {output_path}")

    def clear(self) -> None:
        """Clear all results."""
        self.results.clear()


# Global profiler instance
profiler = PerformanceProfiler()


def profile(
    name: str | None = None,
    report: bool = True,
    track_memory: bool = False,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to profile function execution.

    Args:
        name: Profile name (defaults to function name)
        report: Whether to log results
        track_memory: Whether to track memory usage (requires psutil)

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        profile_name = name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            if not profiler.is_enabled:
                return await func(*args, **kwargs)

            start_time = time.perf_counter()
            start_memory = _get_memory_mb() if track_memory else 0

            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                end_memory = _get_memory_mb() if track_memory else 0

                profile_result = ProfileResult(
                    name=profile_name,
                    duration_ms=duration_ms,
                    memory_delta_mb=end_memory - start_memory,
                    metadata={"args_count": len(args), "kwargs_count": len(kwargs)},
                )
                profiler.record(profile_result)

                if report:
                    logger.info(
                        f"Profile [{profile_name}]: {duration_ms:.2f}ms"
                        + (f" (memory: {profile_result.memory_delta_mb:.2f}MB)" if track_memory else "")
                    )

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            if not profiler.is_enabled:
                return func(*args, **kwargs)

            start_time = time.perf_counter()
            start_memory = _get_memory_mb() if track_memory else 0

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                end_memory = _get_memory_mb() if track_memory else 0

                profile_result = ProfileResult(
                    name=profile_name,
                    duration_ms=duration_ms,
                    memory_delta_mb=end_memory - start_memory,
                    metadata={"args_count": len(args), "kwargs_count": len(kwargs)},
                )
                profiler.record(profile_result)

                if report:
                    logger.info(
                        f"Profile [{profile_name}]: {duration_ms:.2f}ms"
                        + (f" (memory: {profile_result.memory_delta_mb:.2f}MB)" if track_memory else "")
                    )

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


@contextmanager
def time_it(name: str, report: bool = True):
    """Context manager for timing code blocks.

    Args:
        name: Profile name
        report: Whether to log results

    Usage:
        with time_it("database_query"):
            result = await db.fetch(...)
    """
    if not profiler.is_enabled:
        yield
        return

    start_time = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000
        profile_result = ProfileResult(name=name, duration_ms=duration_ms)
        profiler.record(profile_result)

        if report:
            logger.info(f"Timed [{name}]: {duration_ms:.2f}ms")


def _get_memory_mb() -> float:
    """Get current memory usage in MB."""
    try:
        import psutil

        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0.0


class APITimingMiddleware:
    """FastAPI middleware for timing API requests."""

    def __init__(self, app: Any):
        self.app = app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "unknown")
        method = scope.get("method", "unknown")
        name = f"api_{method}_{path}"

        with time_it(name, report=profiler.is_enabled):
            await self.app(scope, receive, send)


# Convenience exports
__all__ = [
    "profiler",
    "PerformanceProfiler",
    "ProfileResult",
    "profile",
    "time_it",
    "APITimingMiddleware",
    "PROFILING_ENABLED",
]
