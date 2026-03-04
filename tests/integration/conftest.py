"""Shared fixtures for integration tests.

Provides real Settings, SourceRegistry, and instrumented variants
for tests that exercise actual adapter chains.
"""

from __future__ import annotations

import os

import pytest

from solstein.config import Settings

# Known test companies from the static catalog
TEST_COMPANY_ID = "accenture"
TEST_COMPANY_NAME = "Accenture"
TEST_TICKER = "ACN"

TEST_MARKET = "Dutch Energy Software"
TEST_SEED = "Eneve"


def has_api_key(env_var: str) -> bool:
    """Check if an API key environment variable is set and non-empty."""
    return bool(os.environ.get(env_var, "").strip())


@pytest.fixture(scope="module")
def real_settings():
    """Load real settings from environment / .env file."""
    return Settings.load()


@pytest.fixture(scope="module")
def real_registry(real_settings):
    """Build the real adapter registry from settings."""
    from solstein.adapters.registry import build_default_registry

    return build_default_registry(real_settings)


@pytest.fixture(scope="module")
def instrumented_registry(real_settings):
    """Build an instrumented registry that records adapter health."""
    from solstein.adapters.instrumented import build_instrumented_registry

    registry, enrichment_wrappers, discovery_wrappers = build_instrumented_registry(real_settings)
    return registry, enrichment_wrappers, discovery_wrappers


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter before each test to avoid cross-test pollution."""
    from solstein.data.security_hardening import rate_limiter

    rate_limiter.client_requests.clear()
    yield
    rate_limiter.client_requests.clear()
