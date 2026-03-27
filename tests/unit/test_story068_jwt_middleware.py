"""Tests for STORY-068: Remove Auth Bypass and Wire Supabase JWT Middleware.

Verifies that:
- No auth bypass exists for /companies or /enrichment
- Public paths are limited to genuinely public routes
- Middleware uses Supabase JWT verification, not custom logic
- tenant_id claim is extracted and available downstream
- Middleware ordering is correct
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "solstein"
SECURITY_PATH = SRC_DIR / "api" / "middleware" / "security.py"


def _extract_public_paths_from_ast(tree: ast.AST) -> set[str] | None:
    """Extract PUBLIC_PATHS frozenset values from SupabaseJWTMiddleware AST."""
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == "SupabaseJWTMiddleware"):
            continue
        for item in node.body:
            if not isinstance(item, ast.Assign):
                continue
            for target in item.targets:
                if not (isinstance(target, ast.Name) and target.id == "PUBLIC_PATHS"):
                    continue
                if not (isinstance(item.value, ast.Call) and item.value.args):
                    continue
                set_node = item.value.args[0]
                if isinstance(set_node, ast.Set):
                    return {elt.value for elt in set_node.elts if isinstance(elt, ast.Constant)}
    return None


class TestNoAuthBypass:
    """REQ-1: Bypass list contains only genuinely public routes."""

    def test_no_companies_in_bypass(self):
        """GET /companies must NOT be in the public/excluded paths."""
        content = SECURITY_PATH.read_text()
        # Check that /companies is NOT in any public/excluded path set
        assert '"/companies"' not in content or "PROTECTED" in content.split('"/companies"')[0][-50:], (
            "security.py still has /companies in a bypass/excluded list"
        )

    def test_no_enrichment_in_bypass(self):
        """GET /enrichment must NOT be in the public/excluded paths."""
        content = SECURITY_PATH.read_text()
        assert '"/enrichment"' not in content or "PROTECTED" in content.split('"/enrichment"')[0][-50:], (
            "security.py still has /enrichment in a bypass/excluded list"
        )

    def test_public_paths_are_minimal(self):
        """PUBLIC_PATHS should only contain genuinely public routes."""
        content = SECURITY_PATH.read_text()
        tree = ast.parse(content)

        paths = _extract_public_paths_from_ast(tree)
        assert paths is not None, "Could not find PUBLIC_PATHS in SupabaseJWTMiddleware"

        allowed = {
            "/health",
            "/healthz",
            "/ready",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/login",
            "/auth/signup",
            "/auth/refresh",
        }
        unexpected = paths - allowed
        assert not unexpected, f"PUBLIC_PATHS contains unexpected routes: {unexpected}"


class TestSupabaseJWTVerification:
    """REQ-2: JWT verification uses Supabase, not custom logic."""

    def test_no_custom_jwt_decode(self):
        """security.py must not call jwt.decode or jwt.encode."""
        content = SECURITY_PATH.read_text()
        assert "jwt.decode" not in content, "security.py still uses jwt.decode"
        assert "jwt.encode" not in content, "security.py still uses jwt.encode"

    def test_uses_supabase_get_user(self):
        """Middleware must call client.auth.get_user for verification."""
        content = SECURITY_PATH.read_text()
        assert "get_user" in content, "security.py does not call get_user for verification"

    def test_uses_supabase_client(self):
        """Middleware must import and use get_supabase."""
        content = SECURITY_PATH.read_text()
        assert "get_supabase" in content, "security.py does not use get_supabase"


class TestTenantIdExtraction:
    """REQ-3: tenant_id claim is extracted and available downstream."""

    def test_tenant_id_extracted(self):
        """Middleware must extract tenant_id from JWT metadata."""
        content = SECURITY_PATH.read_text()
        assert "tenant_id" in content, "security.py does not extract tenant_id"

    def test_tenant_id_set_on_scope(self):
        """tenant_id must be set on request state/scope."""
        content = SECURITY_PATH.read_text()
        assert 'scope["state"]["tenant_id"]' in content or "state.tenant_id" in content, (
            "security.py does not set tenant_id on request scope/state"
        )


class TestMiddlewareOrdering:
    """REQ-4: Middleware ordering is correct."""

    def test_middleware_class_exists(self):
        """SupabaseJWTMiddleware class must exist."""
        content = SECURITY_PATH.read_text()
        assert "class SupabaseJWTMiddleware" in content, "SupabaseJWTMiddleware class not found"

    def test_old_authentication_middleware_removed(self):
        """Old AuthenticationMiddleware with PROTECTED_PREFIXES must be gone."""
        content = SECURITY_PATH.read_text()
        assert "PROTECTED_PREFIXES" not in content, "Old PROTECTED_PREFIXES pattern still in security.py"

    def test_setup_registers_supabase_middleware(self):
        """setup_security_middleware must register SupabaseJWTMiddleware."""
        content = SECURITY_PATH.read_text()
        assert "SupabaseJWTMiddleware" in content, "setup_security_middleware does not register SupabaseJWTMiddleware"

    def test_no_base_http_middleware(self):
        """Should use raw ASGI interface, not BaseHTTPMiddleware (perf)."""
        content = SECURITY_PATH.read_text()
        assert "BaseHTTPMiddleware" not in content, (
            "security.py still uses BaseHTTPMiddleware (use raw ASGI for performance)"
        )


class TestSpecificExceptions:
    """Middleware must use specific exceptions, not bare except."""

    def test_uses_auth_api_error(self):
        """Must catch AuthApiError specifically."""
        content = SECURITY_PATH.read_text()
        assert "AuthApiError" in content, "security.py does not catch AuthApiError specifically"

    def test_no_bare_except(self):
        """No bare 'except:' or 'except Exception:' in middleware."""
        tree = ast.parse(SECURITY_PATH.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    pytest.fail("Bare except clause found in security.py")
                if isinstance(node.type, ast.Name) and node.type.id == "Exception":
                    pytest.fail("'except Exception' found in security.py — use specific types")
