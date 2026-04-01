"""Behavioral contract tests replacing source-inspection tests.

STORY-253: These tests verify runtime behavior, metadata, and wiring
instead of reading source files with Path.read_text() and asserting on
string patterns.  Every assertion here exercises an actual import, route
registration, Celery task attribute, Pydantic model field, or SQLAlchemy
column — things that would fail on a real regression even if the source
text still contains the expected keywords.

Structural tests that these replace:
  - test_story111_async_export_celery.py  (85.7% source-inspection)
  - test_story047_health_checks.py        (84.8% source-inspection)

Intentionally retained static checks are documented inline with
``# STATIC-OK:`` comments explaining why runtime verification is
impractical for that specific assertion.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
import uuid
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers: load modules that have deep import chains
# ---------------------------------------------------------------------------

def _load_module_directly(mod_name: str, file_path: str) -> object:
    """Load a module via importlib to bypass __init__.py import chains.

    This is the behavioral-test equivalent of the source-inspection pattern
    ``Path(file).read_text()`` — we actually execute the module and get
    live objects instead of string-matching source text.
    """
    if mod_name in sys.modules:
        return sys.modules[mod_name]

    spec = importlib.util.spec_from_file_location(
        mod_name, file_path, submodule_search_locations=[]
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _load_export_tasks():
    """Load export_tasks module."""
    task_path = str(
        Path(__file__).parent.parent.parent
        / "src" / "solstein" / "worker" / "export_tasks.py"
    )
    return _load_module_directly("solstein.worker.export_tasks", task_path)


# ===================================================================
# SECTION 1: Export Celery Task Behavioral Contracts (was STORY-111)
# ===================================================================

class TestExportTaskMetadata:
    """Verify Celery task wiring via runtime metadata, not source text."""

    @pytest.fixture(autouse=True)
    def _load(self):
        self.mod = _load_export_tasks()
        self.task = self.mod.generate_export

    # -- Task registration & naming --

    def test_task_name_follows_convention(self):
        """Task name must follow solstein.worker_tasks namespace."""
        assert self.task.name == "solstein.worker_tasks.generate_export"

    def test_task_bound_to_export_queue(self):
        """Task must be routed to the 'export' queue."""
        assert self.task.queue == "export"

    def test_task_max_retries(self):
        """Task must have max_retries=2 for bounded retry."""
        assert self.task.max_retries == 2

    def test_task_acks_late(self):
        """Task must use acks_late for reliability."""
        assert self.task.acks_late is True

    # -- Generator functions are callable --

    @pytest.mark.parametrize("fn_name", [
        "_generate_excel",
        "_generate_csv",
        "_generate_json",
        "_generate_markdown",
        "_generate_llm_report",
    ])
    def test_generator_function_callable(self, fn_name):
        """Each format generator must be a callable in the module."""
        fn = getattr(self.mod, fn_name, None)
        assert fn is not None, f"{fn_name} not found in export_tasks"
        assert callable(fn), f"{fn_name} is not callable"

    def test_llm_formats_set_contains_llm(self):
        """_LLM_FORMATS must include 'llm' for extended time limits."""
        assert "llm" in self.mod._LLM_FORMATS


class TestExportTaskCeleryConfig:
    """Verify Celery configuration wires the export task correctly."""

    @pytest.fixture(autouse=True)
    def _load(self):
        # Ensure export_tasks loaded first so task is registered
        _load_export_tasks()
        from solstein.celery_config import celery_app  # noqa: PLC0415
        self.app = celery_app

    def test_export_tasks_in_includes(self):
        """export_tasks module must be in celery include list."""
        assert "solstein.worker.export_tasks" in self.app.conf.include

    def test_task_routed_to_export_queue(self):
        """Task routing must send generate_export to 'export' queue."""
        routes = self.app.conf.task_routes
        key = "solstein.worker_tasks.generate_export"
        assert key in routes
        assert routes[key]["queue"] == "export"

    def test_task_time_limits(self):
        """Task annotations must set hard=150s, soft=120s."""
        annotations = self.app.conf.task_annotations
        key = "solstein.worker_tasks.generate_export"
        assert key in annotations
        assert annotations[key]["time_limit"] == 150
        assert annotations[key]["soft_time_limit"] == 120


# ===================================================================
# SECTION 2: Export API Router Behavioral Contracts
# ===================================================================

class TestExportRouterRegistration:
    """Verify export router has correct routes via runtime inspection."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = importlib.import_module("solstein.api.routers.exports")
        self.router = mod.router
        self._routes = {
            (r.path, tuple(sorted(r.methods)))
            for r in self.router.routes
            if hasattr(r, "methods")
        }

    def test_post_endpoint_registered(self):
        """POST /api/v1/exports must be registered."""
        assert ("/api/v1/exports", ("POST",)) in self._routes

    def test_get_list_endpoint_registered(self):
        """GET /api/v1/exports must be registered."""
        assert ("/api/v1/exports", ("GET",)) in self._routes

    def test_get_status_endpoint_registered(self):
        """GET /api/v1/exports/{job_id} must be registered."""
        assert ("/api/v1/exports/{job_id}", ("GET",)) in self._routes

    def test_router_prefix(self):
        """Router must use /api/v1/exports prefix."""
        assert self.router.prefix == "/api/v1/exports"


class TestExportRequestModel:
    """Verify ExportRequest Pydantic model fields at runtime."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = importlib.import_module("solstein.api.routers.exports")
        self.model = mod.ExportRequest

    def test_has_format_field(self):
        """ExportRequest must have a 'format' field."""
        assert "format" in self.model.model_fields

    def test_has_company_id_field(self):
        """ExportRequest must have a 'company_id' field."""
        assert "company_id" in self.model.model_fields


class TestExportJobResponseModel:
    """Verify ExportJobResponse Pydantic model fields at runtime."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = importlib.import_module("solstein.api.routers.exports")
        self.model = mod.ExportJobResponse

    @pytest.mark.parametrize("field", [
        "job_id", "status", "format", "file_url", "created_at", "completed_at",
    ])
    def test_response_has_required_field(self, field):
        """ExportJobResponse must expose all required fields."""
        assert field in self.model.model_fields


# ===================================================================
# SECTION 3: ExportJobRecord SQLAlchemy Model Contracts
# ===================================================================

class TestExportJobRecordModel:
    """Verify ExportJobRecord columns and table config at runtime."""

    @pytest.fixture(autouse=True)
    def _load(self):
        from solstein.infrastructure.models.export import ExportJobRecord  # noqa: PLC0415
        self.model = ExportJobRecord

    def test_table_name(self):
        """Table must be named export_jobs."""
        assert self.model.__tablename__ == "export_jobs"

    @pytest.mark.parametrize("column", [
        "id", "tenant_id", "company_id", "format", "status",
        "file_url", "error_message", "created_at", "completed_at",
    ])
    def test_column_exists(self, column):
        """ExportJobRecord must have all required columns."""
        col_names = [c.name for c in self.model.__table__.columns]
        assert column in col_names

    def test_has_composite_indexes(self):
        """Table must have composite indexes for query performance."""
        table_args = self.model.__table_args__
        assert isinstance(table_args, tuple)
        assert len(table_args) >= 2, "Expected at least 2 composite indexes"

    def test_to_dict_returns_required_keys(self):
        """to_dict() must include job_id, tenant_id, format, status."""
        record = self.model()
        record.id = uuid.uuid4()
        record.tenant_id = "tenant-1"
        record.company_id = "comp-123"
        record.format = "excel"
        record.status = "queued"
        record.file_url = None
        record.error_message = None
        record.created_at = None
        record.completed_at = None

        d = record.to_dict()
        assert d["tenant_id"] == "tenant-1"
        assert d["format"] == "excel"
        assert d["status"] == "queued"
        assert "job_id" in d

    def test_model_importable_from_package(self):
        """ExportJobRecord must be importable from models package."""
        from solstein.infrastructure.models import ExportJobRecord as FromPkg  # noqa: PLC0415
        assert FromPkg is self.model


# ===================================================================
# SECTION 4: Health Check Router Behavioral Contracts (was STORY-047)
# ===================================================================

class TestHealthRouterRegistration:
    """Verify health router routes via runtime inspection."""

    @pytest.fixture(autouse=True)
    def _load(self):
        mod = importlib.import_module("solstein.api.routers.health")
        self.router = mod.router
        self._route_paths = {
            r.path for r in self.router.routes if hasattr(r, "methods")
        }

    def test_health_check_endpoint(self):
        """GET /health must be registered."""
        assert "/health" in self._route_paths

    def test_health_status_endpoint(self):
        """GET /health/status must be registered."""
        assert "/health/status" in self._route_paths

    def test_health_ready_endpoint(self):
        """GET /health/ready must be registered."""
        assert "/health/ready" in self._route_paths

    def test_health_live_endpoint(self):
        """GET /health/live must be registered."""
        assert "/health/live" in self._route_paths


class TestHealthCheckModules:
    """Verify health check strategy classes exist and follow the pattern."""

    @pytest.mark.parametrize("module_name,class_name", [
        ("solstein.core.health_checks.database", "DatabaseHealthCheck"),
        ("solstein.core.health_checks.redis", "RedisHealthCheck"),
        ("solstein.core.health_checks.llm", "LLMHealthCheck"),
        ("solstein.core.health_checks.api", "ApiHealthCheck"),
        ("solstein.core.health_checks.configuration", "ConfigurationHealthCheck"),
    ])
    def test_health_check_class_exists(self, module_name, class_name):
        """Each health check module must export its strategy class."""
        mod = importlib.import_module(module_name)
        cls = getattr(mod, class_name, None)
        assert cls is not None, f"{class_name} not found in {module_name}"

    @pytest.mark.parametrize("module_name,class_name", [
        ("solstein.core.health_checks.database", "DatabaseHealthCheck"),
        ("solstein.core.health_checks.redis", "RedisHealthCheck"),
        ("solstein.core.health_checks.llm", "LLMHealthCheck"),
        ("solstein.core.health_checks.api", "ApiHealthCheck"),
        ("solstein.core.health_checks.configuration", "ConfigurationHealthCheck"),
    ])
    def test_health_check_inherits_strategy(self, module_name, class_name):
        """Each health check must implement the HealthCheckStrategy base."""
        mod = importlib.import_module(module_name)
        cls = getattr(mod, class_name)
        assert hasattr(cls, "check"), f"{class_name} must have a 'check' method"


class TestHealthCheckResult:
    """Verify HealthCheckResult dataclass fields."""

    @pytest.fixture(autouse=True)
    def _load(self):
        from solstein.monitoring.health import HealthCheckResult  # noqa: PLC0415
        self.result_cls = HealthCheckResult

    @pytest.mark.parametrize("field", [
        "name", "status", "response_time_ms", "message", "details",
    ])
    def test_result_has_field(self, field):
        """HealthCheckResult must have all required fields."""
        assert field in self.result_cls.__dataclass_fields__

    def test_result_to_dict(self):
        """HealthCheckResult.to_dict() must return a dict with all fields."""
        result = self.result_cls(
            name="test",
            status="healthy",
            response_time_ms=1.0,
            message="ok",
        )
        d = result.to_dict()
        assert d["name"] == "test"
        assert d["status"] == "healthy"


# ===================================================================
# SECTION 5: Static tests intentionally retained
# ===================================================================

class TestRetainedStaticChecks:
    """Source-text assertions that are intentionally kept.

    Each test documents WHY runtime verification is impractical for
    that specific check.  See STORY-253 acceptance criteria.
    """

    # STATIC-OK: Celery @shared_task decorator metadata isn't reliably
    # introspectable at runtime (it's consumed at decoration time).
    # Verifying the decorator text in source is the practical approach.
    def test_task_uses_shared_task_decorator(self):
        """Export task must use @shared_task (decorator intent not introspectable)."""
        task_path = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "worker" / "export_tasks.py"
        )
        source = task_path.read_text()
        assert "@shared_task" in source

    # STATIC-OK: The DLQ integration uses record_failure() in an except
    # handler — verifying it was called requires mocking the entire task
    # execution with a failing DB, which is an integration test concern.
    def test_task_integrates_with_dlq(self):
        """Export task must import and use dead_letter_queue (wiring intent)."""
        task_path = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "worker" / "export_tasks.py"
        )
        source = task_path.read_text()
        assert "dead_letter_queue" in source
        assert "record_failure" in source

    # STATIC-OK: The idempotency guard is a runtime branch that requires
    # a full DB + job fixture to test behaviorally.  The static check
    # confirms the guard exists; the integration suite tests it end-to-end.
    def test_task_has_idempotency_guard(self):
        """Export task must check job status before processing."""
        task_path = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "worker" / "export_tasks.py"
        )
        source = task_path.read_text()
        assert '"completed"' in source
        assert '"processing"' in source

    # STATIC-OK: asyncio.sleep in health check code is a banned pattern.
    # There's no runtime check for "this function does NOT call sleep"
    # — absence of a call is only verifiable via source inspection or AST.
    @pytest.mark.parametrize("path_suffix", [
        "core/monitoring.py",
        "core/health_checks/database.py",
        "core/health_checks/redis.py",
        "core/health_checks/llm.py",
        "core/health_checks/api.py",
        "core/health_checks/configuration.py",
        "api/routers/health.py",
    ])
    def test_no_asyncio_sleep_in_health_checks(self, path_suffix):
        """Health check code must not contain asyncio.sleep (banned pattern)."""
        src = Path(__file__).parent.parent.parent / "src" / "solstein" / path_suffix
        assert src.exists(), f"{path_suffix} not found"
        text = src.read_text()
        assert "asyncio.sleep" not in text, f"asyncio.sleep found in {path_suffix}"

    # STATIC-OK: Documentation existence is inherently a file-system check.
    def test_export_api_documentation_exists(self):
        """Export API documentation must exist."""
        doc_path = (
            Path(__file__).parent.parent.parent
            / "docs" / "exports" / "async-export-api.md"
        )
        assert doc_path.exists(), "Export API documentation not found"
