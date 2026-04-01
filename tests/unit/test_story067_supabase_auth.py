"""Tests for STORY-067: Migrate Authentication to Supabase Auth.

STORY-253 NOTE: These are STRUCTURAL source-inspection tests that verify
auth migration by reading source files. They are intentionally retained as
a secondary defense layer alongside the behavioral contract tests in
test_behavioral_auth_contracts.py which exercise runtime behavior.

Structural tests here catch: accidental re-introduction of legacy patterns
(bcrypt imports, jwt.encode, hash_password functions, demo comments).
They do NOT verify that auth actually works at runtime — see the behavioral
tests for that coverage.

Verifies that:
- Auth endpoints delegate to Supabase Auth SDK
- No custom password hashing exists in auth code
- No custom JWT signing logic exists in auth code
- Login with wrong credentials returns 401
- Token refresh uses Supabase refresh token
- No "# Demo" or "change-me-in-production" patterns remain
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# -- Codebase audit tests (no server needed) ----------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src" / "solstein"


class TestNoCustomPasswordHashing:
    """REQ-1/REQ-4: No custom password hashing in the codebase."""

    def test_no_bcrypt_in_auth_router(self):
        """auth.py must not import bcrypt."""
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        content = auth_path.read_text()
        assert "import bcrypt" not in content, "auth.py still imports bcrypt"
        assert "bcrypt.checkpw" not in content, "auth.py still calls bcrypt.checkpw"
        assert "bcrypt.hashpw" not in content, "auth.py still calls bcrypt.hashpw"

    def test_no_demo_bypass_comment(self):
        """REQ-4: '# Demo' bypass comment must be gone."""
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        content = auth_path.read_text()
        assert "# Demo" not in content, "auth.py still has '# Demo' bypass comment"

    def test_no_custom_jwt_signing_in_auth_router(self):
        """Auth router must not create or sign JWTs locally."""
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        content = auth_path.read_text()
        assert "jwt.encode" not in content, "auth.py still calls jwt.encode"
        assert "jwt_handler" not in content, "auth.py still references jwt_handler"


class TestNoChangeInProductionDefaults:
    """Verify 'change-me-in-production' is gone from config."""

    def test_no_change_me_in_production_in_config(self):
        config_path = SRC_DIR / "config.py"
        content = config_path.read_text()
        assert "change-me-in-production" not in content, "config.py still contains 'change-me-in-production'"


class TestDependenciesUseSupabase:
    """dependencies.py must delegate token verification to Supabase."""

    def test_no_jwt_handler_import(self):
        """dependencies.py must not import jwt_handler (comments are ok)."""
        deps_path = SRC_DIR / "api" / "dependencies.py"
        tree = ast.parse(deps_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_str = ast.dump(node)
                assert "jwt_handler" not in import_str, "dependencies.py still imports jwt_handler"

    def test_imports_supabase_client(self):
        deps_path = SRC_DIR / "api" / "dependencies.py"
        content = deps_path.read_text()
        assert "get_supabase" in content, "dependencies.py does not import get_supabase"


class TestConfigRemovesAdminCredentials:
    """SecurityConfig must not contain admin_email or admin_password_hash as fields."""

    def test_no_admin_email_field_declaration(self):
        """admin_email must not be a Pydantic field in SecurityConfig."""
        config_path = SRC_DIR / "config.py"
        tree = ast.parse(config_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "SecurityConfig":
                field_names = []
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        field_names.append(item.target.id)
                assert "admin_email" not in field_names, "SecurityConfig still declares admin_email as a field"
                return
        pytest.fail("SecurityConfig class not found in config.py")

    def test_no_admin_password_hash_field_declaration(self):
        """admin_password_hash must not be a Pydantic field in SecurityConfig."""
        config_path = SRC_DIR / "config.py"
        tree = ast.parse(config_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "SecurityConfig":
                field_names = []
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        field_names.append(item.target.id)
                assert "admin_password_hash" not in field_names, (
                    "SecurityConfig still declares admin_password_hash as a field"
                )
                return
        pytest.fail("SecurityConfig class not found in config.py")


class TestAuthRouterUsesSupabase:
    """auth.py endpoints must call Supabase Auth SDK."""

    def test_auth_router_imports_supabase(self):
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        content = auth_path.read_text()
        assert "get_supabase" in content, "auth.py does not import get_supabase"

    def test_auth_router_has_login_endpoint(self):
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        content = auth_path.read_text()
        assert "sign_in_with_password" in content, "auth.py login does not call sign_in_with_password"

    def test_auth_router_has_refresh_endpoint(self):
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        content = auth_path.read_text()
        assert "refresh_session" in content, "auth.py refresh does not call refresh_session"

    def test_auth_router_has_signup_endpoint(self):
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        content = auth_path.read_text()
        assert "sign_up" in content, "auth.py does not have a signup endpoint"

    def test_auth_router_has_logout_endpoint(self):
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        content = auth_path.read_text()
        assert "sign_out" in content, "auth.py does not have a logout endpoint using sign_out"


class TestAuthRouterModels:
    """Verify response models are properly defined."""

    def test_auth_token_response_has_refresh_token(self):
        """AuthTokenResponse must include refresh_token (Supabase provides it)."""
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        tree = ast.parse(auth_path.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "AuthTokenResponse":
                field_names = []
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        field_names.append(item.target.id)
                assert "refresh_token" in field_names, "AuthTokenResponse missing refresh_token field"
                assert "access_token" in field_names, "AuthTokenResponse missing access_token field"
                return
        pytest.fail("AuthTokenResponse class not found in auth.py")

    def test_user_info_response_exists(self):
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        content = auth_path.read_text()
        assert "class UserInfoResponse" in content, "UserInfoResponse class not found in auth.py"


class TestNoCustomPasswordHelpersRemain:
    """hash_password and verify_password must be removed from auth.py."""

    def test_no_hash_password_function(self):
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        content = auth_path.read_text()
        assert "def hash_password" not in content, "auth.py still has hash_password function"

    def test_no_verify_password_function(self):
        auth_path = SRC_DIR / "api" / "routers" / "auth.py"
        content = auth_path.read_text()
        assert "def verify_password" not in content, "auth.py still has verify_password function"
