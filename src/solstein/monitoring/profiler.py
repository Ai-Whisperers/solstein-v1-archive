"""Performance profiling and monitoring for Solstein.

EPIC-023: Performance Optimization - Story 1
"""

from __future__ import annotations

import asyncio
import functools
import json
import time
import tracemalloc
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar

from loguru import logger

T = TypeVar("T")


@dataclass
class ProfileResult:
    """Result of a profiling session."""

    name: str
    duration_ms: float
    memory_peak_mb: float | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 2),
            "memory_peak_mb": round(self.memory_peak_mb, 2) if self.memory_peak_mb else None,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class PerformanceProfiler:
    """Central performance profiler for Solstein."""

    _instance: PerformanceProfiler | None = None

    def __new__(cls) -> PerformanceProfiler:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialized = True
        self._results: list[ProfileResult] = []
        self._enabled = False
        self._trace_memory = False

    def enable(self, trace_memory: bool = False) -> None:
        """Enable profiling."""
        self._enabled = True
        self._trace_memory = trace_memory
        logger.info(f"Performance profiling enabled (memory tracing: {trace_memory})")

    def disable(self) -> None:
        """Disable profiling."""
        self._enabled = False
        logger.info("Performance profiling disabled")

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    @contextmanager
    def profile(self, name: str, **metadata: Any):
        """Context manager for profiling a code block."""
        if not self._enabled:
            yield
            return

        start_time = time.perf_counter()
        memory_start = None

        if self._trace_memory:
            tracemalloc.start()
            memory_start = tracemalloc.take_snapshot()

        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000
            memory_peak = None

            if self._trace_memory and memory_start:
                memory_current = tracemalloc.take_snapshot()
                top_stats = memory_current.compare_to(memory_start, "lineno")
                memory_peak = sum(stat.size for stat in top_stats[:5]) / (1024 * 1024)
                tracemalloc.stop()

            result = ProfileResult(
                name=name,
                duration_ms=duration_ms,
                memory_peak_mb=memory_peak,
                metadata=metadata,
            )
            self._results.append(result)

            logger.debug(
                f"Profile [{name}]: {duration_ms:.2f}ms",
                memory_mb=round(memory_peak, 2) if memory_peak else None,
            )

    def get_results(self) -> list[ProfileResult]:
        """Get all profiling results."""
        return self._results.copy()

    def get_summary(self) -> dict[str, Any]:
        """Get summary statistics."""
        if not self._results:
            return {"count": 0}

        durations = [r.duration_ms for r in self._results]
        memories = [r.memory_peak_mb for r in self._results if r.memory_peak_mb]

        summary = {
            "count": len(self._results),
            "total_duration_ms": round(sum(durations), 2),
            "avg_duration_ms": round(sum(durations) / len(durations), 2),
            "max_duration_ms": round(max(durations), 2),
            "min_duration_ms": round(min(durations), 2),
        }

        if memories:
            summary["avg_memory_mb"] = round(sum(memories) / len(memories), 2)
            summary["max_memory_mb"] = round(max(memories), 2)

        return summary

    def export_json(self, path: str) -> None:
        """Export results to JSON."""
        data = {
            "summary": self.get_summary(),
            "results": [r.to_dict() for r in self._results],
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Profiling results exported to {path}")

    def clear(self) -> None:
        """Clear all results."""
        self._results.clear()


# Singleton instance
_profiler = PerformanceProfiler()


def profile(
    name: str | None = None,
    report: bool = False,
    trace_memory: bool = False,
) -> Callable:
    """Decorator for profiling functions.

    Args:
        name: Profile name (defaults to function name)
        report: Whether to log results after execution
        trace_memory: Whether to track memory usage

    Usage:
        @profile(name="enrich_company", report=True)
        async def enrich_company(company_id: str):
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        profile_name = name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            if not _profiler.is_enabled:
                return await func(*args, **kwargs)

            with _profiler.profile(profile_name, function=func.__name__):
                result = await func(*args, **kwargs)

            if report:
                summary = _profiler.get_summary()
                logger.info(f"Profile report for {profile_name}", summary=summary)

            return result

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            if not _profiler.is_enabled:
                return func(*args, **kwargs)

            with _profiler.profile(profile_name, function=func.__name__):
                result = func(*args, **kwargs)

            if report:
                summary = _profiler.get_summary()
                logger.info(f"Profile report for {profile_name}", summary=summary)

            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# Convenience functions
def enable_profiling(trace_memory: bool = False) -> None:
    """Enable performance profiling globally."""
    _profiler.enable(trace_memory=trace_memory)


def disable_profiling() -> None:
    """Disable performance profiling globally."""
    _profiler.disable()


def get_profiler() -> PerformanceProfiler:
    """Get the global profiler instance."""
    return _profiler


# Timing decorator (lightweight, always available)
def timed(name: str | None = None) -> Callable:
    """Lightweight timing decorator that works even when profiling is disabled."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        timer_name = name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.debug(f"[{timer_name}] {elapsed_ms:.2f}ms")

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.debug(f"[{timer_name}] {elapsed_ms:.2f}ms")

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


__all__ = [
    "PerformanceProfiler",
    "ProfileResult",
    "enable_profiling",
    "disable_profiling",
    "get_profiler",
    "profile",
    "timed",
]
