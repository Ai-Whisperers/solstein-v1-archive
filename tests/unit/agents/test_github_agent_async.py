"""Tests for STORY-133: GitHub agent async httpx migration.

Verifies that:
- GitHubClient.get() is async and uses httpx.AsyncClient
- GitHubOrgSearcher methods are async
- DependencyAnalyzer.analyze() is async and fetches concurrently
- GitHubAgent.gather() works end-to-end with async calls
- No `import requests` remains in the github agent package
"""

from __future__ import annotations

import asyncio
import inspect
import time
from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from solstein.agents import github_agent as github_agent_mod
from solstein.agents.github import analyzers as analyzers_mod
from solstein.agents.github import client as client_mod
from solstein.agents.github import search as search_mod
from solstein.agents.github.analyzers import DependencyAnalyzer
from solstein.agents.github.client import GitHubClient
from solstein.agents.github.models import GitHubRepo
from solstein.agents.github.search import GitHubOrgSearcher
from solstein.agents.github_agent import GitHubAgent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fake_response(status_code: int = 200, json_data: Any = None) -> httpx.Response:
    """Create a fake httpx.Response."""
    resp = httpx.Response(
        status_code=status_code,
        json=json_data or {},
        request=httpx.Request("GET", "https://api.github.com/test"),
    )
    return resp


# ---------------------------------------------------------------------------
# Test: No requests import in github agent package
# ---------------------------------------------------------------------------

def test_no_requests_import_in_github_package():
    """STORY-133 AC: No import requests remains in any github agent file."""
    for mod in [client_mod, search_mod, analyzers_mod, github_agent_mod]:
        source = inspect.getsource(mod)
        assert "import requests" not in source, (
            f"Found 'import requests' in {mod.__name__} — "
            "STORY-133 requires all HTTP calls to use httpx"
        )


# ---------------------------------------------------------------------------
# Test: GitHubClient.get is async
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_github_client_get_is_async():
    """STORY-133 AC: GitHubClient.get uses await with httpx.AsyncClient."""
    assert inspect.iscoroutinefunction(GitHubClient.get), (
        "GitHubClient.get must be an async method"
    )


@pytest.mark.asyncio
async def test_github_client_get_returns_response():
    """GitHubClient.get returns httpx.Response via AsyncClient."""
    client = GitHubClient(github_token="test-token")

    mock_resp = _fake_response(200, {"items": []})

    with patch("solstein.agents.github.client.httpx.AsyncClient") as mock_cls:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=mock_resp)
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_instance

        resp = await client.get("https://api.github.com/test")

    assert resp.status_code == 200
    mock_instance.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_github_client_get_retries_without_auth_on_401():
    """GitHubClient retries without auth header on 401."""
    client = GitHubClient(github_token="test-token")

    resp_401 = _fake_response(401, {})
    resp_200 = _fake_response(200, {"login": "acme"})

    call_count = 0

    async def _fake_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return resp_401
        return resp_200

    with patch("solstein.agents.github.client.httpx.AsyncClient") as mock_cls:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(side_effect=_fake_get)
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_instance

        resp = await client.get("https://api.github.com/test")

    assert resp.status_code == 200
    assert call_count == 2


# ---------------------------------------------------------------------------
# Test: GitHubOrgSearcher is async
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_org_searcher_search_is_async():
    """GitHubOrgSearcher.search is async."""
    assert inspect.iscoroutinefunction(GitHubOrgSearcher.search)
    assert inspect.iscoroutinefunction(GitHubOrgSearcher.fetch_repos)


@pytest.mark.asyncio
async def test_org_searcher_search_returns_org():
    """GitHubOrgSearcher.search finds an org via async client."""
    client = GitHubClient(github_token="test")
    searcher = GitHubOrgSearcher(client)

    resp = _fake_response(200, {"items": [{"login": "acme-corp"}]})
    client.get = AsyncMock(return_value=resp)

    result = await searcher.search("Acme Corp")
    assert result == "acme-corp"


@pytest.mark.asyncio
async def test_org_searcher_fetch_repos_returns_list():
    """GitHubOrgSearcher.fetch_repos returns repo list."""
    client = GitHubClient(github_token="test")
    searcher = GitHubOrgSearcher(client)

    repos = [{"name": "repo1", "stargazers_count": 10}]
    resp = _fake_response(200, repos)
    # Second call returns empty to end pagination
    resp_empty = _fake_response(200, [])
    client.get = AsyncMock(side_effect=[resp, resp_empty])

    result = await searcher.fetch_repos("acme-corp")
    assert len(result) == 1
    assert result[0]["name"] == "repo1"


# ---------------------------------------------------------------------------
# Test: DependencyAnalyzer is async
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_dependency_analyzer_is_async():
    """DependencyAnalyzer.analyze is async."""
    assert inspect.iscoroutinefunction(DependencyAnalyzer.analyze)


@pytest.mark.asyncio
async def test_dependency_analyzer_fetches_files_concurrently():
    """STORY-133 AC: DependencyAnalyzer fetches dependency files concurrently."""
    client = GitHubClient(github_token="test")
    analyzer = DependencyAnalyzer(client)

    async def _fake_fetch_file(org: str, repo: str, path: str) -> str | None:
        # Simulate network delay — if sequential, total > 0.2s; if concurrent, ~0.1s
        await asyncio.sleep(0.05)
        if path == "requirements.txt":
            return "requests==2.31.0\nnumpy==1.26.0"
        if path == "package.json":
            return '{"dependencies": {"react": "18.0.0"}}'
        return None

    client.fetch_file = _fake_fetch_file  # type: ignore[assignment]

    repos = [
        GitHubRepo(name="repo1", full_name="acme/repo1", html_url="", description="", language="Python", stars=100, forks=10, open_issues=5, updated_at="2026-01-01"),
        GitHubRepo(name="repo2", full_name="acme/repo2", html_url="", description="", language="JS", stars=50, forks=5, open_issues=2, updated_at="2026-01-01"),
    ]

    start = time.monotonic()
    result = await analyzer.analyze("acme", repos)
    elapsed = time.monotonic() - start

    assert result is not None
    # 2 repos x 2 files = 4 fetches at 0.05s each
    # Sequential: ~0.2s, Concurrent: ~0.05s
    # Allow generous margin for CI overhead
    assert elapsed < 0.15, f"Fetch took {elapsed:.3f}s — should be concurrent, not sequential"


@pytest.mark.asyncio
async def test_dependency_analyzer_parses_deps():
    """DependencyAnalyzer correctly parses fetched dependency files."""
    client = GitHubClient(github_token="test")
    analyzer = DependencyAnalyzer(client)

    async def _fake_fetch(org: str, repo: str, path: str) -> str | None:
        if path == "requirements.txt":
            return "requests==2.31.0\nnumpy>=1.26.0\npandas==2.0.0"
        if path == "package.json":
            return '{"dependencies": {"react": "18.0.0", "lodash": "4.17.21"}, "devDependencies": {"typescript": "5.3.0"}}'
        return None

    client.fetch_file = _fake_fetch  # type: ignore[assignment]

    repos = [
        GitHubRepo(name="r1", full_name="o/r1", html_url="", description="", language="Python", stars=10, forks=1, open_issues=0, updated_at="2026-01-01"),
    ]

    result = await analyzer.analyze("o", repos)
    assert result is not None
    assert result.python["count"] == 3
    assert result.javascript["count"] == 3  # 2 deps + 1 devDep


# ---------------------------------------------------------------------------
# Test: GitHubAgent.gather end-to-end
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_github_agent_gather_end_to_end():
    """GitHubAgent.gather works with fully async pipeline."""
    agent = GitHubAgent(github_token="test")

    # Mock the searcher
    agent.searcher.search = AsyncMock(return_value="acme-corp")
    agent.searcher.fetch_repos = AsyncMock(return_value=[
        {
            "name": "main-repo",
            "full_name": "acme-corp/main-repo",
            "html_url": "https://github.com/acme-corp/main-repo",
            "description": "Main repo",
            "language": "Python",
            "stargazers_count": 500,
            "forks_count": 50,
            "open_issues_count": 10,
            "default_branch": "main",
            "updated_at": "2026-01-01T00:00:00Z",
        }
    ])

    # Mock dependency analyzer (async)
    agent.dep_analyzer.client.fetch_file = AsyncMock(return_value=None)

    result = await agent.gather("Acme Corp", {})

    assert result.success is True
    assert result.agent_name == "GitHubAgent"
    assert len(result.raw_sources) >= 1
    assert len(result.extracted_facts) >= 1  # At least tech_stack


@pytest.mark.asyncio
async def test_github_agent_gather_no_org_found():
    """GitHubAgent returns gracefully when no org found."""
    agent = GitHubAgent(github_token="test")
    agent.searcher.search = AsyncMock(return_value=None)

    result = await agent.gather("Nonexistent Company", {})

    assert result.success is False
    assert "organization" in (result.error_message or "").lower()
    assert "found" in (result.error_message or "").lower()


# ---------------------------------------------------------------------------
# Test: httpx.AsyncClient is used as context manager
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_async_client_used_as_context_manager():
    """STORY-133 AC: AsyncClient used as async context manager."""
    source = inspect.getsource(GitHubClient.get)
    assert "async with" in source, (
        "GitHubClient.get must use 'async with httpx.AsyncClient()' "
        "for proper connection management"
    )
    assert "AsyncClient" in source


# ---------------------------------------------------------------------------
# Test: Timeout uses httpx-native approach
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_timeout_is_passed_to_httpx():
    """STORY-133 AC: Timeout configuration uses httpx-native approach."""
    client = GitHubClient(github_token="test")

    mock_resp = _fake_response(200, {})

    with patch("solstein.agents.github.client.httpx.AsyncClient") as mock_cls:
        mock_instance = AsyncMock()
        mock_instance.get = AsyncMock(return_value=mock_resp)
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = mock_instance

        await client.get("https://api.github.com/test", timeout=42.0)

    call_kwargs = mock_instance.get.call_args
    assert call_kwargs is not None
    # Timeout should be passed as a keyword argument
    assert "timeout" in call_kwargs.kwargs or (len(call_kwargs.args) > 3)
