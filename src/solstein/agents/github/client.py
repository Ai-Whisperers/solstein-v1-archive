"""GitHub API client."""

from __future__ import annotations

from typing import Any

import httpx

from ..resilience import GITHUB_RETRY_CONFIG, CircuitBreaker, call_with_retry


class GitHubClient:
    """GitHub API client with resilience patterns."""

    def __init__(self, github_token: str | None = None):
        self.github_token = github_token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Solstein-AI",
        }
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"

        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0,
            name="GitHubAPI",
        )

    def _request_headers(self, unauthenticated: bool = False) -> dict[str, str]:
        headers = dict(self.headers)
        if unauthenticated:
            headers.pop("Authorization", None)
        return headers

    def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        timeout: float = 15,
        unauthenticated: bool = False,
    ) -> httpx.Response:
        """Make GET request to GitHub API."""
        import httpx

        headers = self._request_headers(unauthenticated)

        with httpx.Client() as client:
            resp = client.get(url, headers=headers, params=params, timeout=timeout)

        if resp.status_code == 401 and "Authorization" in self.headers and not unauthenticated:
            # Retry without auth
            return self.get(url, params=params, timeout=timeout, unauthenticated=True)

        return resp

    def fetch_file(self, org: str, repo: str, path: str) -> str | None:
        """Fetch file contents from repo."""
        import base64

        url = f"{self.api_base}/repos/{org}/{repo}/contents/{path}"

        try:
            resp = self.get(url, timeout=10)
            if resp.status_code != 200:
                return None

            data = resp.json()
            content = data.get("content")
            encoding = data.get("encoding")

            if not isinstance(content, str) or encoding != "base64":
                return None

            raw = base64.b64decode(content.encode("utf-8"))
            return raw.decode("utf-8", errors="replace")

        except Exception:
            return None
