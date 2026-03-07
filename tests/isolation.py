"""Test isolation fixtures and utilities.

EPIC-029 Story 2: Ensure test isolation and prevent cross-test contamination.

Usage:
    # In conftest.py
    from tests.isolation import db_isolation, clean_cache

    @pytest.fixture(autouse=True)
    async def isolated_db(db_session):
        async with db_isolation(db_session):
            yield
"""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from solstein.infrastructure.cache import get_cache


@asynccontextmanager
async def db_isolation(session: AsyncSession) -> AsyncGenerator[None, None]:
    """Provide database transaction isolation for tests.

    Automatically rolls back any changes after test completes.

    Args:
        session: Database session.

    Yields:
        None
    """
    try:
        yield
    finally:
        # Rollback all changes
        await session.rollback()
        # Close any open transactions
        await session.close()


@asynccontextmanager
async def clean_cache() -> AsyncGenerator[None, None]:
    """Clean cache before and after test.

    Yields:
        None
    """
    cache = get_cache()
    await cache.clear()
    try:
        yield
    finally:
        await cache.clear()


class TestTimer:
    """Time test execution for slow test detection."""

    def __init__(self, max_duration_ms: float = 1000.0):
        """Initialize timer.

        Args:
            max_duration_ms: Maximum acceptable duration in milliseconds.
        """
        self.max_duration_ms = max_duration_ms
        self.start_time: float = 0
        self.end_time: float = 0

    def start(self):
        """Start timing."""
        import time

        self.start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop timing and return duration.

        Returns:
            Duration in milliseconds.
        """
        import time

        self.end_time = time.perf_counter()
        return (self.end_time - self.start_time) * 1000

    def is_slow(self) -> bool:
        """Check if test was slow.

        Returns:
            True if test exceeded max duration.
        """
        duration = (self.end_time - self.start_time) * 1000
        return duration > self.max_duration_ms


@pytest.fixture(autouse=True)
async def isolated_database(db_session: AsyncSession):
    """Ensure database isolation for all tests.

    Args:
        db_session: Database session fixture.

    Yields:
        Database session.
    """
    async with db_isolation(db_session):
        yield db_session


@pytest.fixture(autouse=True)
async def clean_redis_cache():
    """Clean cache before and after each test."""
    async with clean_cache():
        yield


@pytest.fixture
def time_test():
    """Fixture to time test execution.

    Yields:
        TestTimer instance.
    """
    timer = TestTimer()
    timer.start()
    yield timer
    duration = timer.stop()
    if timer.is_slow():
        pytest.warn(f"Test took {duration:.2f}ms (threshold: {timer.max_duration_ms}ms)")


class MockLLMProvider:
    """Mock LLM provider for isolated testing."""

    def __init__(self, responses: dict[str, str] | None = None):
        """Initialize mock provider.

        Args:
            responses: Predefined responses by prompt pattern.
        """
        self.responses = responses or {}
        self.calls: list[dict[str, Any]] = []

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock response.

        Args:
            prompt: Input prompt.
            **kwargs: Additional parameters.

        Returns:
            Mock response.
        """
        self.calls.append({"prompt": prompt, "kwargs": kwargs})

        # Check for predefined response
        for pattern, response in self.responses.items():
            if pattern in prompt:
                return response

        # Default response
        return f"Mock response for: {prompt[:50]}..."


@pytest.fixture
def mock_llm():
    """Fixture providing mock LLM provider.

    Yields:
        MockLLMProvider instance.
    """
    provider = MockLLMProvider()
    yield provider


class DeterministicUUID:
    """Generate deterministic UUIDs for tests."""

    def __init__(self, seed: int = 42):
        """Initialize with seed.

        Args:
            seed: Random seed.
        """
        import random

        self.rng = random.Random(seed)

    def uuid4(self) -> str:
        """Generate deterministic UUID.

        Returns:
            UUID string.
        """
        # Generate 16 random bytes
        random_bytes = bytes(self.rng.randint(0, 255) for _ in range(16))
        # Set version (4) and variant bits
        random_bytes = (
            random_bytes[:6]
            + bytes([0x40 | (random_bytes[6] & 0x0F)])
            + random_bytes[7:8]
            + bytes([0x80 | (random_bytes[8] & 0x3F)])
            + random_bytes[9:]
        )
        # Format as UUID
        return (
            random_bytes[:4].hex()
            + "-"
            + random_bytes[4:6].hex()
            + "-"
            + random_bytes[6:8].hex()
            + "-"
            + random_bytes[8:10].hex()
            + "-"
            + random_bytes[10:].hex()
        )


@pytest.fixture
def deterministic_uuids():
    """Fixture providing deterministic UUID generator.

    Yields:
        DeterministicUUID instance.
    """
    yield DeterministicUUID()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
