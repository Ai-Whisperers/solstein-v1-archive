"""HTTP client for the Solstein API.

STORY-118: All CLI commands use this client to call the API via HTTP
rather than importing domain layers directly. This ensures CLI operations
go through authentication, middleware, rate limiting, and audit logging.
"""

from __future__ import annotations

from typing import Any

import httpx

from solstein.cli.auth import get_access_token, get_api_url

# Default HTTP timeout (seconds). Duplicated from shared.constants to avoid
# depending on shared/ which may not yet be merged.
DEFAULT_HTTP_TIMEOUT_S: int = 30


class APIError(Exception):
    """Raised when the API returns a non-success status code."""

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API error {status_code}: {detail}")


class SolsteinAPIClient:
    """Synchronous HTTP client for the Solstein API.

    All requests include the stored auth token (if available) and
    go through the standard API middleware stack.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        token: str | None = None,
    ) -> None:
        self._base_url = (base_url or get_api_url()).rstrip("/")
        self._token = token or get_access_token()
        self._timeout = DEFAULT_HTTP_TIMEOUT_S

    def _headers(self) -> dict[str, str]:
        """Build request headers including auth if available."""
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _handle_response(self, resp: httpx.Response) -> Any:
        """Parse response, raising APIError on non-2xx status."""
        if resp.status_code >= 400:
            try:
                body = resp.json()
                detail = body.get("detail", resp.text)
            except (ValueError, KeyError):
                detail = resp.text
            raise APIError(resp.status_code, str(detail))
        if resp.status_code == 204:
            return None
        return resp.json()

    def get(self, path: str, **params: Any) -> Any:
        """HTTP GET request to the API."""
        with httpx.Client(timeout=self._timeout) as client:
            resp = client.get(
                f"{self._base_url}{path}",
                headers=self._headers(),
                params=params or None,
            )
        return self._handle_response(resp)

    def post(self, path: str, body: dict[str, Any] | None = None) -> Any:
        """HTTP POST request to the API."""
        with httpx.Client(timeout=self._timeout) as client:
            resp = client.post(
                f"{self._base_url}{path}",
                headers=self._headers(),
                json=body,
            )
        return self._handle_response(resp)

    # -- High-level helpers ---------------------------------------------------

    def login(self, email: str, password: str) -> dict[str, Any]:
        """Authenticate and return token payload."""
        return self.post("/auth/login", {"email": email, "password": password})

    def list_companies(self, **params: Any) -> list[dict[str, Any]]:
        """GET /companies — paginated company list."""
        return self.get("/companies", **params)

    def get_company(self, company_id: str) -> dict[str, Any]:
        """GET /companies/{id}."""
        return self.get(f"/companies/{company_id}")

    def start_research(self, company_name: str) -> dict[str, Any]:
        """POST /jobs/research — start a research job."""
        return self.post("/jobs/research", {"company_name": company_name})

    def get_job_status(self, job_id: str) -> dict[str, Any]:
        """GET /jobs/{id} — poll job status."""
        return self.get(f"/jobs/{job_id}")

    def start_export(
        self,
        company_id: str,
        fmt: str = "excel",
    ) -> dict[str, Any]:
        """POST /export — start an export job."""
        return self.post("/export", {"company_id": company_id, "format": fmt})

    def health(self) -> dict[str, Any]:
        """GET /healthz."""
        return self.get("/healthz")
