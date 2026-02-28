#!/usr/bin/env python3
"""Simple test script for LLM health checker without full test dependencies."""

import asyncio
import sys
from datetime import datetime, timedelta, timezone

# Add src to path
sys.path.insert(0, "/home/ai-whisperers/solstein/src")

from solstein.llm.health_checker import (
    ProviderError,
    ProviderErrorType,
    ProviderHealth,
    ProviderHealthChecker,
    ProviderStatus,
)


def test_health_status():
    """Test ProviderHealth status tracking."""
    print("Testing ProviderHealth...")

    # Test healthy provider
    health = ProviderHealth(
        provider="openai",
        status=ProviderStatus.HEALTHY,
    )
    assert health.is_available, "Healthy provider should be available"
    assert health.should_retry, "Healthy provider should allow retry"
    print("  ✓ Healthy provider checks passed")

    # Test rate limited provider
    future_time = datetime.now(timezone.utc) + timedelta(seconds=60)
    health = ProviderHealth(
        provider="openai",
        status=ProviderStatus.RATE_LIMITED,
        retry_after=future_time,
    )
    assert not health.is_available, "Rate limited provider should not be available"
    assert health.should_retry, "Rate limited provider should be retried"
    print("  ✓ Rate limited provider checks passed")

    # Test exhausted provider
    health = ProviderHealth(
        provider="openai",
        status=ProviderStatus.EXHAUSTED,
        estimated_credits_remaining=False,
    )
    assert not health.is_available, "Exhausted provider should not be available"
    print("  ✓ Exhausted provider checks passed")

    print("All ProviderHealth tests passed!\n")


def test_error_classification():
    """Test error classification."""
    print("Testing error classification...")

    checker = ProviderHealthChecker()

    test_cases = [
        ("Rate limit exceeded (429)", ProviderErrorType.RATE_LIMIT, 429),
        ("Too many requests, retry after 60s", ProviderErrorType.RATE_LIMIT, 429),
        ("Invalid API key (401)", ProviderErrorType.AUTHENTICATION, 401),
        ("Authentication failed", ProviderErrorType.AUTHENTICATION, 401),
        ("You exceeded your current quota", ProviderErrorType.QUOTA_EXHAUSTED, 402),
        ("insufficient credits remaining", ProviderErrorType.QUOTA_EXHAUSTED, 402),
        ("Connection timeout", ProviderErrorType.TIMEOUT, None),
        ("Network unreachable", ProviderErrorType.NETWORK_ERROR, None),
        ("Some random error", ProviderErrorType.UNKNOWN, None),
    ]

    for error_msg, expected_type, expected_code in test_cases:
        error = Exception(error_msg)
        result = checker._classify_error(error, "openai")
        assert result.error_type == expected_type, f"Expected {expected_type}, got {result.error_type} for: {error_msg}"
        if expected_code:
            assert result.status_code == expected_code, f"Expected status {expected_code} for: {error_msg}"
        print(f"  ✓ Correctly classified: {error_msg[:40]}...")

    print("All error classification tests passed!\n")


def test_health_updates():
    """Test health status updates."""
    print("Testing health updates...")

    checker = ProviderHealthChecker()

    # Test error update - rate limit
    error = ProviderError(
        error_type=ProviderErrorType.RATE_LIMIT,
        message="Rate limited",
        retry_after_seconds=120,
        provider="openai",
    )
    health = checker._update_health_on_error("openai", error)
    assert health.status == ProviderStatus.RATE_LIMITED
    assert health.retry_after is not None
    print("  ✓ Rate limit update correct")

    # Test error update - quota exhausted
    error = ProviderError(
        error_type=ProviderErrorType.QUOTA_EXHAUSTED,
        message="Quota exceeded",
        provider="openai",
    )
    health = checker._update_health_on_error("openai", error)
    assert health.status == ProviderStatus.EXHAUSTED
    assert health.estimated_credits_remaining is False
    print("  ✓ Quota exhausted update correct")

    # Test success update
    checker._health["groq"] = ProviderHealth(
        provider="groq",
        status=ProviderStatus.DEGRADED,
        consecutive_failures=3,
    )
    health = checker._update_health_on_success("groq")
    assert health.status == ProviderStatus.HEALTHY
    assert health.consecutive_failures == 0
    print("  ✓ Success update correct")

    print("All health update tests passed!\n")


def test_provider_selection():
    """Test provider selection logic."""
    print("Testing provider selection...")

    checker = ProviderHealthChecker()

    # Set up multiple providers
    for provider in ["ollama", "fireworks", "openai", "groq"]:
        checker._health[provider] = ProviderHealth(
            provider=provider,
            status=ProviderStatus.HEALTHY,
        )

    # Test best provider (priority order)
    best = checker.get_best_provider()
    assert best == "ollama", f"Expected ollama (highest priority), got {best}"
    print("  ✓ Best provider selection correct")

    # Test with unavailable providers
    checker._health["ollama"] = ProviderHealth(
        provider="ollama",
        status=ProviderStatus.UNHEALTHY,
    )
    checker._health["fireworks"] = ProviderHealth(
        provider="fireworks",
        status=ProviderStatus.EXHAUSTED,
    )

    best = checker.get_best_provider()
    assert best == "openai", f"Expected openai (first available), got {best}"
    print("  ✓ Provider skips unavailable correctly")

    # Test available list
    available = checker.get_available_providers()
    assert "ollama" not in available, "Unavailable provider should not be in list"
    assert "openai" in available, "Available provider should be in list"
    print("  ✓ Available providers list correct")

    print("All provider selection tests passed!\n")


def test_retry_delays():
    """Test retry delay calculations."""
    print("Testing retry delays...")

    checker = ProviderHealthChecker()

    # Test rate limit retry delay
    future_time = datetime.now(timezone.utc) + timedelta(seconds=45)
    checker._health["openai"] = ProviderHealth(
        provider="openai",
        status=ProviderStatus.RATE_LIMITED,
        retry_after=future_time,
    )
    delay = checker.get_retry_delay("openai")
    assert 40 <= delay <= 50, f"Expected ~45s delay, got {delay}"
    print("  ✓ Rate limit retry delay correct")

    # Test exponential backoff
    checker._health["groq"] = ProviderHealth(
        provider="groq",
        status=ProviderStatus.DEGRADED,
        consecutive_failures=2,
    )
    delay = checker.get_retry_delay("groq")
    assert delay == 4.0, f"Expected 4.0s (2^2), got {delay}"
    print("  ✓ Exponential backoff correct")

    # Test max backoff cap
    checker._health["fireworks"] = ProviderHealth(
        provider="fireworks",
        status=ProviderStatus.DEGRADED,
        consecutive_failures=10,
    )
    delay = checker.get_retry_delay("fireworks")
    assert delay <= 60.0, f"Expected max 60s, got {delay}"
    print("  ✓ Max backoff cap correct")

    print("All retry delay tests passed!\n")


async def test_ollama_check():
    """Test Ollama health check (will fail if Ollama not running)."""
    print("Testing Ollama health check...")

    checker = ProviderHealthChecker()

    # This will likely fail since Ollama isn't running in test environment
    health = await checker.check_ollama()

    # Should still return a valid health object
    assert health.provider == "ollama"
    # Status will depend on whether Ollama is running
    print(f"  ✓ Ollama check returned status: {health.status.value}")
    print("Ollama check test passed!\n")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running LLM Health Checker Tests")
    print("=" * 60 + "\n")

    try:
        test_health_status()
        test_error_classification()
        test_health_updates()
        test_provider_selection()
        test_retry_delays()

        # Async test
        asyncio.run(test_ollama_check())

        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
