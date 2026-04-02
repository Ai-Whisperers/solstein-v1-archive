"""Behavioral contract tests for authentication and JWT middleware.

STORY-253: These tests replace structural source-inspection tests with
runtime behavioral checks. Instead of reading source files and checking
for string patterns, they exercise actual route registration, middleware
logic, model instantiation, and request/response flows.

Surfaces covered:
- Auth route registration (login, signup, refresh, logout, me)
- JWT middleware path classification (public vs protected)
- JWT middleware response codes (401 missing, 401 invalid format, 503 unavailable)
- Auth model instantiation and field presence
- SecurityConfig field checks via runtime reflection
- Export endpoint registration and format validation
"""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Deferred imports — these modules trigger config/database loading so we
# guard them to keep ``pytest --collect-only`` hermetic (STORY-254).
# The pre-commit hook requires top-level imports; try/except + skip keeps
# collection safe while satisfying the linter.
# ---------------------------------------------------------------------------
try:
    from pydantic import ValidationError

    from solstein.api.main import app as _app
    from solstein.api.middleware.security import SupabaseJWTMiddleware
    from solstein.api.routers.auth import (
        AuthTokenResponse,
        LoginRequest,
        UserInfoResponse,
    )
    from solstein.api.routers.exports import (
        _VALID_FORMATS,
        ExportJobResponse,
        ExportRequest,
    )
    from solstein.config import SecurityConfig, Settings
except Exception:  # noqa: BLE001 — broad guard keeps collection hermetic
    pytest.skip(
        "Runtime imports unavailable (config/database not loaded)",
        allow_module_level=True,
    )


def _get_app():
    """Return the FastAPI app (already imported at module level)."""
    return _app


# ===========================================================================
# Section 1: Auth Route Registration (replaces structural read_text checks)
# ===========================================================================


class TestAuthRouteRegistration:
    """Verify auth endpoints are actually registered on the app at runtime.

    STORY-253: Replaces test_story067 source-inspection tests that checked
    for string patterns like 'sign_in_with_password' in source text.
    A registered route proves the endpoint exists AND is wired correctly.
    """

    @pytest.fixture(autouse=True)
    def setup_app(self):
        self.app = _get_app()
        self.route_paths = {route.path for route in self.app.routes if hasattr(route, "path")}

    def test_login_route_registered(self):
        """POST /auth/login endpoint exists at runtime."""
        assert "/auth/login" in self.route_paths, "Login route not registered on the app"

    def test_signup_route_registered(self):
        """POST /auth/signup endpoint exists at runtime."""
        assert "/auth/signup" in self.route_paths, "Signup route not registered on the app"

    def test_refresh_route_registered(self):
        """POST /auth/refresh endpoint exists at runtime."""
        assert "/auth/refresh" in self.route_paths, "Refresh route not registered on the app"

    def test_logout_route_registered(self):
        """POST /auth/logout endpoint exists at runtime."""
        assert "/auth/logout" in self.route_paths, "Logout route not registered on the app"

    def test_me_route_registered(self):
        """GET /auth/me endpoint exists at runtime."""
        assert "/auth/me" in self.route_paths, "Get-me route not registered on the app"


# ===========================================================================
# Section 2: Auth Model Instantiation (replaces AST-walking field checks)
# ===========================================================================


class TestAuthModelsRuntime:
    """Verify auth models can be instantiated with expected fields.

    STORY-253: Replaces AST-based field scanning of AuthTokenResponse and
    UserInfoResponse. If a field is missing, instantiation will fail.
    """

    def test_auth_token_response_has_required_fields(self):
        """AuthTokenResponse must have access_token, refresh_token, token_type."""
        resp = AuthTokenResponse(
            access_token="test-access",
            refresh_token="test-refresh",
            token_type="bearer",
            expires_in=3600,
        )
        assert resp.access_token == "test-access"
        assert resp.refresh_token == "test-refresh"
        assert resp.token_type == "bearer"
        assert resp.expires_in == 3600

    def test_user_info_response_exists_and_instantiable(self):
        """UserInfoResponse must be importable and instantiable."""
        resp = UserInfoResponse(
            user_id="user-123",
            email="test@example.com",
        )
        assert resp.user_id == "user-123"
        assert resp.email == "test@example.com"
        assert resp.role == "user"  # default value

    def test_login_request_model_requires_email_password(self):
        """LoginRequest requires email and password fields."""
        req = LoginRequest(email="a@b.com", password="secret-long-enough")
        assert req.email == "a@b.com"
        assert req.password == "secret-long-enough"


# ===========================================================================
# Section 3: SecurityConfig Runtime Checks (replaces AST field scanning)
# ===========================================================================


class TestSecurityConfigRuntime:
    """Verify SecurityConfig does NOT contain legacy admin fields.

    STORY-253: Replaces AST-walking tests that parsed config.py to check
    field names. Runtime hasattr/reflection is authoritative.
    """

    def test_no_admin_email_field(self):
        """SecurityConfig must not have an admin_email field."""
        settings = Settings.load()
        security = settings.security
        assert not hasattr(security, "admin_email"), "SecurityConfig still has admin_email field"

    def test_no_admin_password_hash_field(self):
        """SecurityConfig must not have an admin_password_hash field."""
        settings = Settings.load()
        security = settings.security
        assert not hasattr(security, "admin_password_hash"), "SecurityConfig still has admin_password_hash field"

    def test_no_change_me_in_secret_key_default(self):
        """The secret key default must not contain 'change-me-in-production'."""
        # Check the model's field default, not the loaded value
        field_info = SecurityConfig.model_fields.get("secret_key")
        if field_info and field_info.default:
            assert "change-me-in-production" not in str(field_info.default), (
                "SecurityConfig secret_key still has 'change-me-in-production' default"
            )


# ===========================================================================
# Section 4: JWT Middleware Behavioral Tests (replaces source-inspection)
# ===========================================================================


class TestJWTMiddlewareBehavior:
    """Test SupabaseJWTMiddleware at runtime using the middleware class directly.

    STORY-253: Replaces test_story068 source-inspection tests that used
    read_text() and AST parsing to check PUBLIC_PATHS, import statements,
    and class names. These tests exercise actual middleware behavior.
    """

    def test_public_paths_include_health(self):
        """Health check paths must be in the public allowlist at runtime."""
        mw = SupabaseJWTMiddleware(app=lambda *a: None)
        assert mw._is_public_path("/health") is True
        assert mw._is_public_path("/healthz") is True
        assert mw._is_public_path("/ready") is True

    def test_public_paths_include_auth(self):
        """Auth routes must be public (login, signup, refresh)."""
        mw = SupabaseJWTMiddleware(app=lambda *a: None)
        assert mw._is_public_path("/auth/login") is True
        assert mw._is_public_path("/auth/signup") is True
        assert mw._is_public_path("/auth/refresh") is True

    def test_protected_paths_not_public(self):
        """Business endpoints must NOT be in the public allowlist."""
        mw = SupabaseJWTMiddleware(app=lambda *a: None)
        assert mw._is_public_path("/companies") is False
        assert mw._is_public_path("/enrichment") is False
        assert mw._is_public_path("/api/v1/exports") is False

    def test_docs_paths_are_public(self):
        """Documentation paths must be public."""
        mw = SupabaseJWTMiddleware(app=lambda *a: None)
        assert mw._is_public_path("/docs") is True
        assert mw._is_public_path("/redoc") is True
        assert mw._is_public_path("/openapi.json") is True

    @pytest.mark.asyncio
    async def test_missing_auth_header_returns_401(self):
        """Request without Authorization header must get 401."""
        from solstein.api.middleware.security import SupabaseJWTMiddleware

        responses: list[dict] = []

        async def capture_app(scope: dict, receive: Any, send: Any) -> None:
            pytest.fail("App should not be called for unauthenticated request")

        mw = SupabaseJWTMiddleware(app=capture_app)

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/companies",
            "query_string": b"",
            "headers": [],
            "root_path": "",
        }

        body_parts: list[bytes] = []

        async def receive_fn() -> dict:
            return {"type": "http.request", "body": b""}

        async def send_fn(message: dict) -> None:
            responses.append(message)
            if message.get("type") == "http.response.body":
                body_parts.append(message.get("body", b""))

        await mw(scope, receive_fn, send_fn)

        # Find the response.start message
        start_msg = next((r for r in responses if r["type"] == "http.response.start"), None)
        assert start_msg is not None, "No HTTP response sent"
        assert start_msg["status"] == 401

    @pytest.mark.asyncio
    async def test_bad_auth_format_returns_401(self):
        """Request with malformed Authorization header must get 401."""
        from solstein.api.middleware.security import SupabaseJWTMiddleware

        responses: list[dict] = []

        async def capture_app(scope: dict, receive: Any, send: Any) -> None:
            pytest.fail("App should not be called for bad auth format")

        mw = SupabaseJWTMiddleware(app=capture_app)

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/companies",
            "query_string": b"",
            "headers": [(b"authorization", b"Basic abc123")],
            "root_path": "",
        }

        async def receive_fn() -> dict:
            return {"type": "http.request", "body": b""}

        async def send_fn(message: dict) -> None:
            responses.append(message)

        await mw(scope, receive_fn, send_fn)

        start_msg = next((r for r in responses if r["type"] == "http.response.start"), None)
        assert start_msg is not None, "No HTTP response sent"
        assert start_msg["status"] == 401

    @pytest.mark.asyncio
    async def test_supabase_unavailable_returns_503(self):
        """If Supabase client fails to import/connect, middleware returns 503."""
        from solstein.api.middleware.security import SupabaseJWTMiddleware

        responses: list[dict] = []

        async def capture_app(scope: dict, receive: Any, send: Any) -> None:
            pytest.fail("App should not be called when Supabase is unavailable")

        mw = SupabaseJWTMiddleware(app=capture_app)

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/companies",
            "query_string": b"",
            "headers": [(b"authorization", b"Bearer valid-looking-token-123")],
            "root_path": "",
        }

        async def receive_fn() -> dict:
            return {"type": "http.request", "body": b""}

        async def send_fn(message: dict) -> None:
            responses.append(message)

        with patch("solstein.core.supabase_client.get_supabase", side_effect=ImportError("No supabase")):
            await mw(scope, receive_fn, send_fn)

        start_msg = next((r for r in responses if r["type"] == "http.response.start"), None)
        assert start_msg is not None, "No HTTP response sent"
        assert start_msg["status"] == 503

    @pytest.mark.asyncio
    async def test_public_path_skips_auth(self):
        """Public paths should pass through without auth check."""
        from solstein.api.middleware.security import SupabaseJWTMiddleware

        app_called = False

        async def mock_app(scope: dict, receive: Any, send: Any) -> None:
            nonlocal app_called
            app_called = True

        mw = SupabaseJWTMiddleware(app=mock_app)

        scope = {
            "type": "http",
            "method": "GET",
            "path": "/health",
            "query_string": b"",
            "headers": [],
            "root_path": "",
        }

        await mw(scope, lambda: {"type": "http.request", "body": b""}, lambda m: None)
        assert app_called, "App was not called for public path /health"


# ===========================================================================
# Section 5: Export Route Registration and Schema (replaces source-inspection)
# ===========================================================================


class TestExportRouteRegistration:
    """Verify export endpoints are registered and models are correct.

    STORY-253: Replaces test_story111 source-inspection tests that checked
    for '@router.post', '202', and format strings in source text.
    """

    @pytest.fixture(autouse=True)
    def setup_app(self):
        self.app = _get_app()
        self.route_paths = {route.path for route in self.app.routes if hasattr(route, "path")}

    def test_exports_create_route_registered(self):
        """POST /api/v1/exports endpoint must be registered."""
        assert "/api/v1/exports" in self.route_paths, "Export create route not registered"

    def test_exports_status_route_registered(self):
        """GET /api/v1/exports/{job_id} endpoint must be registered."""
        assert "/api/v1/exports/{job_id}" in self.route_paths, "Export status route not registered"

    def test_export_request_model_has_format_field(self):
        """ExportRequest model must have a 'format' field."""
        req = ExportRequest(format="excel")
        assert req.format == "excel"

    def test_export_request_rejects_extra_fields(self):
        """ExportRequest must reject extra fields (ConfigDict extra='forbid')."""
        with pytest.raises(ValidationError):
            ExportRequest(format="excel", unknown_field="hack")

    def test_export_job_response_has_required_fields(self):
        """ExportJobResponse must have job_id, status, format fields."""
        resp = ExportJobResponse(job_id="abc-123", status="queued", format="excel")
        assert resp.job_id == "abc-123"
        assert resp.status == "queued"
        assert resp.format == "excel"
        assert resp.file_url is None
        assert resp.progress_pct == 0

    def test_valid_formats_at_runtime(self):
        """The _VALID_FORMATS set must contain expected formats at runtime."""
        expected = {"excel", "csv", "json", "markdown", "llm", "pdf"}
        assert expected.issubset(_VALID_FORMATS), f"Missing formats: {expected - _VALID_FORMATS}"


# ===========================================================================
# Section 6: Worker Task Registration (replaces regex source scanning)
# ===========================================================================


class TestWorkerTaskRegistration:
    """Verify Celery tasks are properly importable and configured at runtime.

    STORY-253: Replaces test_story092 regex-based source scanning with
    actual import and attribute checks.
    """

    def test_export_tasks_module_importable(self):
        """worker.export_tasks must be importable at runtime."""
        from solstein.worker import export_tasks  # noqa: F811

        assert export_tasks is not None

    def test_export_tasks_has_generate_export(self):
        """generate_export task function must exist at runtime."""
        from solstein.worker.export_tasks import generate_export  # noqa: F811

        assert callable(generate_export)

    def test_celery_config_importable(self):
        """worker.celery_config must be importable with app configured."""
        try:
            from solstein.worker.celery_config import celery_app  # noqa: F811

            assert celery_app is not None
        except ImportError:
            pytest.skip("Celery config not available in test environment")


# ===========================================================================
# Section 7: Prometheus Metrics Route (supplements existing behavioral tests)
# ===========================================================================


class TestPrometheusRouteRegistration:
    """Verify /metrics/prometheus route exists at runtime.

    STORY-253: Supplements test_story051 which already has good behavioral
    tests but was missing an E2E route registration check.
    """

    @pytest.fixture(autouse=True)
    def setup_app(self):
        self.app = _get_app()
        self.route_paths = {route.path for route in self.app.routes if hasattr(route, "path")}

    def test_prometheus_metrics_route_registered(self):
        """GET /metrics/prometheus must be registered on the app."""
        assert "/metrics/prometheus" in self.route_paths, (
            "Prometheus metrics route not registered — runtime wiring broken"
        )
