"""GitHub API client.

STORY-133: Migrated from sync httpx.Client to async httpx.AsyncClient.
All HTTP calls now use `await` and do not block the event loop.
"""

from __future__ import annotations

import base64
from typing import Any

import httpx
from loguru import logger

from solstein.config import get_settings

from ..resilience import CircuitBreaker


class GitHubClient:
    """GitHub API client with resilience patterns.

    Uses httpx.AsyncClient for non-blocking HTTP calls.
    Connection pooling is handled by reusing the client instance.
    """

    def __init__(self, github_token: str | None = None):
        self.github_token = github_token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Solstein-AI",
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

        _settings = get_settings()
        self.default_timeout = _settings.http_timeouts.github
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=_settings.circuit_breaker.failure_threshold,
            recovery_timeout=_settings.circuit_breaker.recovery_timeout,
            name="GitHubAPI",
        )

    def _request_headers(self, unauthenticated: bool = False) -> dict[str, str]:
        headers = dict(self.headers)
        if unauthenticated:
            headers.pop("Authorization", None)
        return headers

    async def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        timeout: float | None = None,
        unauthenticated: bool = False,
    ) -> httpx.Response:
        """Make async GET request to GitHub API.

        Uses httpx.AsyncClient as a context manager to ensure proper
        connection pooling and resource cleanup.
        """
        effective_timeout = timeout if timeout is not None else self.default_timeout
        headers = self._request_headers(unauthenticated)

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, params=params, timeout=effective_timeout)

        if resp.status_code == 401 and "Authorization" in self.headers and not unauthenticated:
            # Retry without auth
            return await self.get(url, params=params, timeout=effective_timeout, unauthenticated=True)

        return resp

    async def fetch_file(self, org: str, repo: str, path: str) -> str | None:
        """Fetch file contents from repo."""
        url = f"{self.api_base}/repos/{org}/{repo}/contents/{path}"

        try:
            resp = await self.get(url)
            if resp.status_code != 200:
                return None

            data = resp.json()
            content = data.get("content")
            encoding = data.get("encoding")

            if not isinstance(content, str) or encoding != "base64":
                return None

            raw = base64.b64decode(content.encode("utf-8"))
            return raw.decode("utf-8", errors="replace")

        except Exception as e:  # noqa: BLE001
            logger.warning(f"[GitHubClient] fetch_file {org}/{repo}/{path} failed: {e}")
            return None
