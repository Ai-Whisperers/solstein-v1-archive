"""Fixtures for the LLM evaluation test suite — STORY-056.

Live-LLM tests are marked with @pytest.mark.llm_eval and automatically
skip when ANTHROPIC_API_KEY is not set in the environment.  The fixtures
here create real Anthropic client instances so evaluation tests can call
the API without any mocking.

Run only live tests:
    pytest -m llm_eval tests/llm_eval/ -v

Run only non-live (framework unit) tests:
    pytest -m "not llm_eval" tests/llm_eval/ -v

Run everything (skips live tests silently if key absent):
    pytest tests/llm_eval/ -v
"""

from __future__ import annotations

import os

import pytest

try:
    from anthropic import AsyncAnthropic

    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False
    AsyncAnthropic = None  # type: ignore[assignment,misc]


# ---------------------------------------------------------------------------
# Skip guard — applied automatically to every llm_eval-marked test
# ---------------------------------------------------------------------------


def pytest_collection_modifyitems(config, items):  # noqa: ANN001
    """Skip all llm_eval tests when ANTHROPIC_API_KEY is absent."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return
    skip_reason = pytest.mark.skip(reason="ANTHROPIC_API_KEY not set — set it to run live LLM evaluation tests")
    for item in items:
        if item.get_closest_marker("llm_eval"):
            item.add_marker(skip_reason)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def anthropic_api_key() -> str:
    """Return the Anthropic API key, or skip if absent."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return key


@pytest.fixture(scope="session")
def anthropic_client(anthropic_api_key: str):  # noqa: ANN201
    """Return a real AsyncAnthropic client for live evaluation runs."""
    if not _ANTHROPIC_AVAILABLE or AsyncAnthropic is None:
        pytest.skip("anthropic package not installed — install it with: pip install anthropic")
    return AsyncAnthropic(api_key=anthropic_api_key)


@pytest.fixture(scope="session")
def eval_model() -> str:
    """Model used for live evaluation runs.

    Override via SOLSTEIN_EVAL_MODEL env var to use a different model
    (e.g. claude-haiku-4-5-20251001 for cheaper evaluation runs).
    """
    return os.environ.get("SOLSTEIN_EVAL_MODEL", "claude-haiku-4-5-20251001")
