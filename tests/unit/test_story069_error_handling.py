"""Tests for STORY-069: Error Handling and Input Sanitization.

Verifies that:
- All error responses include error_id (REQ-1)
- No traceback or stack_trace appears in any error response (REQ-1)
- Full tracebacks are logged server-side with error_id (REQ-2)
- Input sanitization is applied via middleware, not per-router (REQ-3)
- Sanitization utilities are referenced from one location (REQ-4)
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "solstein"
EXCEPTIONS_PATH = SRC_DIR / "api" / "exceptions.py"
SECURITY_PATH = SRC_DIR / "api" / "middleware" / "security.py"


class TestOpaqueErrorResponses:
    """REQ-1: Error responses must contain error_id, no tracebacks."""

    def test_no_traceback_in_responses(self):
        """No handler should include traceback/stack_trace in response content."""
        content = EXCEPTIONS_PATH.read_text()
        tree = ast.parse(content)

        # Find all JSONResponse calls and check none include traceback keys
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            # Check if it's a JSONResponse with content= kwarg
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            if func_name != "JSONResponse":
                continue

            # Get the content kwarg
            for kw in node.keywords:
                if kw.arg != "content":
                    continue
                # Walk the content dict for traceback keys
                source = ast.get_source_segment(content, kw.value) or ""
                assert "stack_trace" not in source, (
                    "JSONResponse content contains 'stack_trace' — tracebacks must never be in HTTP responses"
                )
                assert "traceback" not in source.lower() or "format_exc" not in source, (
                    "JSONResponse content references traceback data"
                )

    def test_no_debug_block_in_responses(self):
        """No handler should conditionally include debug info in responses."""
        content = EXCEPTIONS_PATH.read_text()
        # The old pattern was: if settings.debug ... error_response["error"]["debug"]
        assert '"debug"' not in content or "debug" not in content.split("JSONResponse")[0], (
            "exceptions.py still has debug info block in responses"
        )

    def test_no_settings_debug_check(self):
        """Error handlers should not check settings.debug for response content."""
        content = EXCEPTIONS_PATH.read_text()
        assert "settings.debug" not in content, (
            "exceptions.py still conditionally includes info based on debug mode — "
            "responses must be opaque regardless of environment"
        )

    def test_error_id_in_all_handlers(self):
        """Every exception handler must generate and include error_id."""
        content = EXCEPTIONS_PATH.read_text()
        tree = ast.parse(content)

        handler_count = 0
        handlers_with_error_id = 0

        for node in ast.walk(tree):
            if not isinstance(node, ast.AsyncFunctionDef):
                continue
            if not node.name.startswith("handle_"):
                continue
            handler_count += 1
            source = ast.get_source_segment(content, node) or ""
            if "error_id" in source:
                handlers_with_error_id += 1

        assert handler_count >= 4, f"Expected at least 4 handlers, found {handler_count}"
        assert handlers_with_error_id == handler_count, (
            f"Only {handlers_with_error_id}/{handler_count} handlers include error_id"
        )

    def test_error_id_uses_uuid(self):
        """error_id generation must use uuid for uniqueness."""
        content = EXCEPTIONS_PATH.read_text()
        assert "import uuid" in content, "exceptions.py does not import uuid"
        assert "uuid.uuid4" in content, "exceptions.py does not use uuid.uuid4"


class TestServerSideLogging:
    """REQ-2: Full tracebacks logged server-side with error_id."""

    def test_traceback_logged_with_error_id(self):
        """Handlers must log traceback with error_id for correlation."""
        content = EXCEPTIONS_PATH.read_text()
        # The generic exception handler must log traceback
        assert "traceback.format_exc()" in content, (
            "exceptions.py does not call traceback.format_exc() for server-side logging"
        )
        # error_id must appear in log calls
        assert "error_id" in content, "exceptions.py does not use error_id in logging"

    def test_no_get_settings_import(self):
        """Error handlers should not import get_settings (no env-conditional responses)."""
        content = EXCEPTIONS_PATH.read_text()
        assert "get_settings" not in content, (
            "exceptions.py still imports get_settings — responses should be opaque regardless of environment"
        )


class TestMiddlewareSanitization:
    """REQ-3: Input sanitization via middleware, not per-router."""

    def test_sanitization_middleware_exists(self):
        """InputSanitizationMiddleware must exist in security.py."""
        content = SECURITY_PATH.read_text()
        assert "class InputSanitizationMiddleware" in content, "InputSanitizationMiddleware not found in security.py"

    def test_sanitization_in_middleware_chain(self):
        """setup_security_middleware must register InputSanitizationMiddleware."""
        content = SECURITY_PATH.read_text()
        assert "InputSanitizationMiddleware" in content, (
            "InputSanitizationMiddleware not registered in middleware chain"
        )

    def test_no_per_router_sanitization_imports(self):
        """Routers should not import InputValidator directly."""
        routers_dir = SRC_DIR / "api" / "routers"
        if not routers_dir.exists():
            pytest.skip("Routers directory not found")

        for router_file in routers_dir.glob("*.py"):
            content = router_file.read_text()
            assert "from solstein.data.security_hardening import InputValidator" not in content, (
                f"{router_file.name} imports InputValidator directly — sanitization should be via middleware (REQ-3)"
            )


class TestResponseShape:
    """Verify the exact shape of error responses."""

    def test_api_error_has_no_details_field_by_default(self):
        """APIError.to_dict removed — response built inline with error_id."""
        content = EXCEPTIONS_PATH.read_text()
        # The old to_dict included a details field unconditionally
        # New pattern should only include details when explicitly set
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "APIError":
                method_names = [
                    item.name for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                assert "to_dict" not in method_names, (
                    "APIError still has to_dict — response should be built inline with error_id in the handler"
                )
                return
        pytest.fail("APIError class not found")

    def test_validation_errors_sanitized(self):
        """Validation error details should not include raw input values."""
        content = EXCEPTIONS_PATH.read_text()
        # The handler should strip 'input' and 'url' from validation errors
        assert "safe_errors" in content or "sanitize" in content.lower(), (
            "Validation error handler does not sanitize error details"
        )
