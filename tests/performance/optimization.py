"""Test performance optimization utilities.

EPIC-029 Story 7: Optimize test execution speed.

Usage:
    # Mark slow tests
    @pytest.mark.slow
    def test_heavy_computation():
        pass

    # Run only fast tests during development
    pytest -m "not slow"
"""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import pytest


# Test markers
slow = pytest.mark.slow
fast = pytest.mark.fast
integration = pytest.mark.integration
e2e = pytest.mark.e2e
unit = pytest.mark.unit


def measure_test_duration(func: Callable) -> Callable:
    """Decorator to measure test duration.

    Args:
        func: Test function.

    Returns:
        Wrapped function.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        print(f"⏱️  {func.__name__}: {duration:.3f}s")
        return result

    return wrapper


class TestProfiler:
    """Profile test execution time."""

    def __init__(self):
        """Initialize profiler."""
        self.timings: dict[str, list[float]] = {}

    def record(self, test_name: str, duration: float):
        """Record test timing.

        Args:
            test_name: Test name.
            duration: Duration in seconds.
        """
        if test_name not in self.timings:
            self.timings[test_name] = []
        self.timings[test_name].append(duration)

    def get_slow_tests(self, threshold_seconds: float = 1.0) -> list[tuple[str, float]]:
        """Get slowest tests.

        Args:
            threshold_seconds: Threshold for "slow".

        Returns:
            List of (test_name, avg_duration) tuples.
        """
        averages = []
        for test_name, durations in self.timings.items():
            avg = sum(durations) / len(durations)
            if avg > threshold_seconds:
                averages.append((test_name, avg))

        return sorted(averages, key=lambda x: x[1], reverse=True)

    def print_summary(self):
        """Print timing summary."""
        if not self.timings:
            return

        print("\n" + "=" * 60)
        print("TEST TIMING SUMMARY")
        print("=" * 60)

        slow_tests = self.get_slow_tests()
        if slow_tests:
            print("\nSlow tests (>1s):")
            for name, duration in slow_tests[:10]:
                print(f"  {duration:.2f}s - {name}")

        total_time = sum(sum(d) for d in self.timings.values())
        avg_time = total_time / sum(len(d) for d in self.timings.values())
        print(f"\nTotal test time: {total_time:.2f}s")
        print(f"Average per test: {avg_time:.3f}s")
        print("=" * 60)


# Global profiler
_profiler = TestProfiler()


def get_profiler() -> TestProfiler:
    """Get global profiler instance.

    Returns:
        TestProfiler.
    """
    return _profiler


@pytest.fixture(scope="session", autouse=True)
def report_test_performance(request):
    """Report test performance at end of session."""
    yield
    _profiler.print_summary()
