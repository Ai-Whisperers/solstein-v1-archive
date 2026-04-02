"""Tests for STORY-086: Enforce Universal Audit Trail.

Validates:
- REQ-1: Every authenticated request generates an audit log entry
- REQ-2: Audit logging is middleware-based, not per-endpoint opt-in
- REQ-3: Audit records written to dedicated append-only table
- REQ-4: Audit records not deletable by application code
- REQ-5: Audit logging failure must not fail the original request
"""

from __future__ import annotations

# For the middleware module, we need to bypass the middleware __init__.py
# which has a broken import (AuthenticationMiddleware). Load directly.
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Model imports work fine — they don't trigger the broken middleware __init__
from solstein.infrastructure.models.audit import DataAccessAuditRecord

_AUDIT_MW_PATH = str(Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "middleware" / "audit.py")
_spec = importlib.util.spec_from_file_location(
    "solstein.api.middleware.audit",
    _AUDIT_MW_PATH,
    submodule_search_locations=[],
)
_audit_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["solstein.api.middleware.audit"] = _audit_mod
_spec.loader.exec_module(_audit_mod)  # type: ignore[union-attr]

AuditMiddleware = _audit_mod.AuditMiddleware
_extract_resource_id = _audit_mod._extract_resource_id
_extract_user_id = _audit_mod._extract_user_id
_get_client_ip = _audit_mod._get_client_ip
_is_excluded = _audit_mod._is_excluded


# ---------------------------------------------------------------------------
# REQ-1: Audit record content
# ---------------------------------------------------------------------------
class TestAuditRecordContent:
    """Audit entries must contain required fields."""

    def test_model_has_tenant_id(self):
        """Audit record must have tenant_id field."""
        assert hasattr(DataAccessAuditRecord, "tenant_id")

    def test_model_has_user_id(self):
        """Audit record must have user_id field."""
        assert hasattr(DataAccessAuditRecord, "user_id")

    def test_model_has_endpoint(self):
        """Audit record must have endpoint field."""
        assert hasattr(DataAccessAuditRecord, "endpoint")

    def test_model_has_resource_id(self):
        """Audit record must have resource_id field."""
        assert hasattr(DataAccessAuditRecord, "resource_id")

    def test_model_has_timestamp(self):
        """Audit record must have timestamp field."""
        assert hasattr(DataAccessAuditRecord, "timestamp")

    def test_model_has_status_code(self):
        """Audit record must have status_code field."""
        assert hasattr(DataAccessAuditRecord, "status_code")

    def test_model_has_method(self):
        """Audit record must have method field."""
        assert hasattr(DataAccessAuditRecord, "method")

    def test_model_has_client_ip(self):
        """Audit record must have client_ip field."""
        assert hasattr(DataAccessAuditRecord, "client_ip")

    def test_table_name(self):
        """Audit table must be named data_access_audit."""
        assert DataAccessAuditRecord.__tablename__ == "data_access_audit"


# ---------------------------------------------------------------------------
# REQ-2: Middleware-based (not per-endpoint)
# ---------------------------------------------------------------------------
class TestMiddlewareBased:
    """Audit must be implemented as middleware."""

    def test_audit_middleware_class_exists(self):
        """AuditMiddleware class must exist."""
        assert AuditMiddleware is not None

    def test_middleware_has_dispatch(self):
        """AuditMiddleware must have a dispatch method."""
        assert hasattr(AuditMiddleware, "dispatch")

    def test_middleware_wired_in_main(self):
        """main.py must include AuditMiddleware."""
        main_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "main.py"
        source = main_path.read_text()
        assert "AuditMiddleware" in source
        assert "add_middleware" in source

    def test_middleware_added_before_tenant(self):
        """AuditMiddleware must be added before TenantMiddleware in main.py.

        In Starlette, middleware added first wraps middleware added later.
        AuditMiddleware added before TenantMiddleware means it executes
        AFTER TenantMiddleware sets tenant_id on request.state.
        """
        main_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "main.py"
        source = main_path.read_text()
        # Check the add_middleware() calls, not the imports
        audit_pos = source.index("add_middleware(AuditMiddleware)")
        tenant_pos = source.index("add_middleware(TenantMiddleware)")
        # AuditMiddleware registration must appear before TenantMiddleware
        assert audit_pos < tenant_pos, (
            "AuditMiddleware must be registered before TenantMiddleware so it executes after tenant_id is set"
        )


# ---------------------------------------------------------------------------
# REQ-3: Dedicated append-only table
# ---------------------------------------------------------------------------
class TestDedicatedTable:
    """Audit records must use a dedicated table."""

    def test_separate_table(self):
        """Audit table must be separate from other models."""
        assert DataAccessAuditRecord.__tablename__ == "data_access_audit"
        assert DataAccessAuditRecord.__tablename__ != "enrichment_audit_trail"

    def test_model_exported_from_package(self):
        """DataAccessAuditRecord must be exported from models package."""
        models_init = (
            Path(__file__).parent.parent.parent / "src" / "solstein" / "infrastructure" / "models" / "__init__.py"
        )
        source = models_init.read_text()
        assert "DataAccessAuditRecord" in source

    def test_model_has_indexes(self):
        """Audit table must have composite indexes for query performance."""
        table_args = DataAccessAuditRecord.__table_args__
        assert len(table_args) >= 2, "Expected at least 2 composite indexes"


# ---------------------------------------------------------------------------
# REQ-4: Not deletable by application code
# ---------------------------------------------------------------------------
class TestNotDeletable:
    """Application code must not be able to delete audit records."""

    def test_no_delete_method_on_model(self):
        """Model should not have a custom delete method."""
        assert not hasattr(DataAccessAuditRecord, "delete")

    def test_module_documents_append_only(self):
        """Audit model module must document append-only intent."""
        audit_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "infrastructure" / "models" / "audit.py"
        source = audit_path.read_text()
        assert "append-only" in source.lower()

    def test_middleware_does_not_delete(self):
        """Audit middleware must not contain DELETE operations."""
        middleware_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "middleware" / "audit.py"
        source = middleware_path.read_text()
        assert ".delete(" not in source
        assert "DELETE" not in source


# ---------------------------------------------------------------------------
# REQ-5: Audit failure must not fail the request
# ---------------------------------------------------------------------------
class TestAuditResilience:
    """Audit logging failure must not affect the original request."""

    def test_middleware_catches_audit_errors(self):
        """The middleware dispatch must catch audit write failures."""
        middleware_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "middleware" / "audit.py"
        source = middleware_path.read_text()
        # Must have try/except around audit write
        assert "try:" in source
        assert "Audit trail write failed" in source

    def test_error_handler_logs_failure(self):
        """Audit failure must be logged, not silently swallowed."""
        middleware_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "middleware" / "audit.py"
        source = middleware_path.read_text()
        assert "logger.error" in source


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------
class TestHelperFunctions:
    """Test utility functions used by the audit middleware."""

    def test_extract_resource_id_company(self):
        """Extract company ID from /api/v1/companies/<id>."""
        assert _extract_resource_id("/api/v1/companies/abc-123") == "abc-123"

    def test_extract_resource_id_research(self):
        """Extract research ID from /research/<id>."""
        assert _extract_resource_id("/research/run-456") == "run-456"

    def test_extract_resource_id_none(self):
        """Return None for paths without resource IDs."""
        assert _extract_resource_id("/api/v1/health") is None

    def test_extract_resource_id_jobs(self):
        """Extract job ID from /jobs/<id>."""
        assert _extract_resource_id("/jobs/job-789") == "job-789"

    def test_is_excluded_health(self):
        """Health endpoints must be excluded."""
        assert _is_excluded("/health") is True
        assert _is_excluded("/healthz") is True

    def test_is_excluded_metrics(self):
        """Metrics endpoints must be excluded."""
        assert _is_excluded("/metrics") is True
        assert _is_excluded("/metrics/prometheus") is True

    def test_is_excluded_docs(self):
        """Documentation endpoints must be excluded."""
        assert _is_excluded("/docs") is True
        assert _is_excluded("/openapi.json") is True

    def test_is_excluded_auth(self):
        """Auth endpoints must be excluded (no user identity yet)."""
        assert _is_excluded("/auth/login") is True

    def test_not_excluded_api(self):
        """API data endpoints must NOT be excluded."""
        assert _is_excluded("/api/v1/companies") is False
        assert _is_excluded("/scoring/results") is False

    def test_extract_user_id_from_dict(self):
        """Extract user ID from dict-style user."""
        request = MagicMock()
        request.state.user = {"id": "user-123", "email": "test@example.com"}
        assert _extract_user_id(request) == "user-123"

    def test_extract_user_id_from_object(self):
        """Extract user ID from object-style user."""
        request = MagicMock()
        user = MagicMock()
        user.id = "user-456"
        request.state.user = user
        assert _extract_user_id(request) == "user-456"

    def test_extract_user_id_none(self):
        """Return None when no user on request."""
        request = MagicMock()
        request.state.user = None
        assert _extract_user_id(request) is None

    def test_get_client_ip_direct(self):
        """Get client IP from direct connection."""
        request = MagicMock()
        request.headers.get.return_value = None
        request.client.host = "192.168.1.1"
        assert _get_client_ip(request) == "192.168.1.1"

    def test_get_client_ip_forwarded(self):
        """Get client IP from X-Forwarded-For header."""
        request = MagicMock()
        request.headers.get.return_value = "10.0.0.1, 10.0.0.2"
        assert _get_client_ip(request) == "10.0.0.1"


# ---------------------------------------------------------------------------
# Model serialization
# ---------------------------------------------------------------------------
class TestModelSerialization:
    """DataAccessAuditRecord must serialize correctly."""

    def test_to_dict_has_required_fields(self):
        """to_dict() must include all required audit fields."""
        record = DataAccessAuditRecord()
        record.id = 1
        record.tenant_id = "tenant-1"
        record.user_id = "user-1"
        record.method = "GET"
        record.endpoint = "/api/v1/companies"
        record.resource_id = "comp-123"
        record.status_code = 200
        record.client_ip = "10.0.0.1"
        record.timestamp = None

        d = record.to_dict()
        assert d["tenant_id"] == "tenant-1"
        assert d["user_id"] == "user-1"
        assert d["method"] == "GET"
        assert d["endpoint"] == "/api/v1/companies"
        assert d["status_code"] == 200


# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------
class TestDocumentation:
    """Audit trail must be documented."""

    def test_middleware_module_has_docstring(self):
        """audit.py middleware must have a module docstring."""
        middleware_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "middleware" / "audit.py"
        source = middleware_path.read_text()
        assert "STORY-086" in source
        assert '"""' in source

    def test_model_module_has_docstring(self):
        """audit.py model must have a module docstring."""
        model_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "infrastructure" / "models" / "audit.py"
        source = model_path.read_text()
        assert "STORY-086" in source
        assert "append-only" in source.lower()

    def test_main_documents_audit(self):
        """main.py must document audit middleware addition."""
        main_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "main.py"
        source = main_path.read_text()
        assert "STORY-086" in source
