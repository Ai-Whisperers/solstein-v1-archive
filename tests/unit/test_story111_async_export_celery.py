"""Tests for STORY-111: Move Exports to Async Celery Tasks.

.. deprecated:: STORY-253
   The source-inspection tests in this file (85.7% of assertions read source
   with ``Path.read_text()``) have been superseded by behavioral contract
   tests in ``test_behavioral_contracts.py`` which verify runtime metadata,
   route registration, Celery task attributes, and Pydantic model fields.

   This file is retained for backward-compatibility during the transition.
   New export-related contract tests should go in ``test_behavioral_contracts.py``.

Validates:
- REQ-1: POST /api/v1/exports returns 202 with job_id within 1s
- REQ-2: Export Celery task exists on the 'export' queue
- REQ-3: GET /api/v1/exports/{job_id} returns status and download URL
- REQ-4: Failed exports appear in DLQ
- REQ-5: Re-triggering same export job is idempotent
"""

from __future__ import annotations

import importlib.util
import sys
import uuid
from pathlib import Path

from solstein.infrastructure.models.export import ExportJobRecord

# Load the export task module directly to avoid __init__.py chain issues
_EXPORT_TASKS_PATH = str(
    Path(__file__).parent.parent.parent
    / "src" / "solstein" / "worker" / "export_tasks.py"
)
_spec = importlib.util.spec_from_file_location(
    "solstein.worker.export_tasks", _EXPORT_TASKS_PATH,
    submodule_search_locations=[],
)
_export_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["solstein.worker.export_tasks"] = _export_mod
_spec.loader.exec_module(_export_mod)  # type: ignore[union-attr]

generate_export = _export_mod.generate_export
_LLM_FORMATS = _export_mod._LLM_FORMATS

# Load the API router module directly
_EXPORTS_ROUTER_PATH = str(
    Path(__file__).parent.parent.parent
    / "src" / "solstein" / "api" / "routers" / "exports.py"
)


# ---------------------------------------------------------------------------
# REQ-1: POST /api/v1/exports returns 202 with job_id
# ---------------------------------------------------------------------------
class TestExportEndpointStructure:
    """The export API must be properly structured."""

    def test_router_module_exists(self):
        """exports.py router module must exist."""
        router_path = Path(_EXPORTS_ROUTER_PATH)
        assert router_path.exists(), "exports.py router not found"

    def test_post_endpoint_defined(self):
        """POST endpoint must be defined in exports.py."""
        source = Path(_EXPORTS_ROUTER_PATH).read_text()
        assert "@router.post" in source
        assert "202" in source or "HTTP_202_ACCEPTED" in source

    def test_get_endpoint_defined(self):
        """GET endpoint must be defined in exports.py."""
        source = Path(_EXPORTS_ROUTER_PATH).read_text()
        assert "@router.get" in source
        assert "job_id" in source

    def test_router_has_prefix(self):
        """Router must use /api/v1/exports prefix."""
        source = Path(_EXPORTS_ROUTER_PATH).read_text()
        assert "/api/v1/exports" in source

    def test_export_request_model_defined(self):
        """ExportRequest pydantic model must exist."""
        source = Path(_EXPORTS_ROUTER_PATH).read_text()
        assert "class ExportRequest" in source
        assert "format" in source

    def test_export_response_model_defined(self):
        """ExportJobResponse pydantic model must exist."""
        source = Path(_EXPORTS_ROUTER_PATH).read_text()
        assert "class ExportJobResponse" in source
        assert "job_id" in source
        assert "status" in source

    def test_valid_formats_defined(self):
        """Valid formats must include standard export types."""
        source = Path(_EXPORTS_ROUTER_PATH).read_text()
        assert "excel" in source
        assert "csv" in source
        assert "json" in source
        assert "markdown" in source
        assert "llm" in source


# ---------------------------------------------------------------------------
# REQ-2: Export Celery task on 'export' queue
# ---------------------------------------------------------------------------
class TestCeleryTaskStructure:
    """The export Celery task must be properly configured."""

    def test_task_module_exists(self):
        """export_tasks.py must exist in worker package."""
        task_path = Path(_EXPORT_TASKS_PATH)
        assert task_path.exists()

    def test_generate_export_function_exists(self):
        """generate_export task function must exist."""
        assert generate_export is not None

    def test_task_has_shared_task_decorator(self):
        """Task must use @shared_task decorator."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "@shared_task" in source

    def test_task_configured_for_export_queue(self):
        """Task must be configured for the export queue."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert 'queue="export"' in source

    def test_task_has_retry_config(self):
        """Task must have retry configuration."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "max_retries" in source

    def test_task_has_bind_true(self):
        """Task must use bind=True for self access."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "bind=True" in source

    def test_task_has_acks_late(self):
        """Task must use acks_late for reliability."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "acks_late=True" in source

    def test_task_name_follows_convention(self):
        """Task name must follow solstein.worker_tasks namespace."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "solstein.worker_tasks.generate_export" in source

    def test_llm_formats_defined(self):
        """LLM formats set must be defined for higher time limits."""
        assert "llm" in _LLM_FORMATS

    def test_task_registered_in_worker_tasks(self):
        """generate_export must be re-exported from worker_tasks.py."""
        worker_tasks_path = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "worker_tasks.py"
        )
        source = worker_tasks_path.read_text()
        assert "generate_export" in source

    def test_task_included_in_celery_config(self):
        """export_tasks module must be in celery_config includes."""
        config_path = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "celery_config.py"
        )
        source = config_path.read_text()
        assert "solstein.worker.export_tasks" in source


# ---------------------------------------------------------------------------
# REQ-3: GET /api/v1/exports/{job_id} returns status and URL
# ---------------------------------------------------------------------------
class TestExportJobModel:
    """ExportJobRecord must have the required fields and behavior."""

    def test_model_has_id(self):
        """Export job must have id field."""
        assert hasattr(ExportJobRecord, "id")

    def test_model_has_tenant_id(self):
        """Export job must have tenant_id field."""
        assert hasattr(ExportJobRecord, "tenant_id")

    def test_model_has_company_id(self):
        """Export job must have company_id field."""
        assert hasattr(ExportJobRecord, "company_id")

    def test_model_has_format(self):
        """Export job must have format field."""
        assert hasattr(ExportJobRecord, "format")

    def test_model_has_status(self):
        """Export job must have status field."""
        assert hasattr(ExportJobRecord, "status")

    def test_model_has_file_url(self):
        """Export job must have file_url field."""
        assert hasattr(ExportJobRecord, "file_url")

    def test_model_has_error_message(self):
        """Export job must have error_message field."""
        assert hasattr(ExportJobRecord, "error_message")

    def test_model_has_created_at(self):
        """Export job must have created_at field."""
        assert hasattr(ExportJobRecord, "created_at")

    def test_model_has_completed_at(self):
        """Export job must have completed_at field."""
        assert hasattr(ExportJobRecord, "completed_at")

    def test_table_name(self):
        """Table must be named export_jobs."""
        assert ExportJobRecord.__tablename__ == "export_jobs"

    def test_model_has_indexes(self):
        """Table must have composite indexes for query performance."""
        table_args = ExportJobRecord.__table_args__
        assert len(table_args) >= 2, "Expected at least 2 composite indexes"

    def test_model_exported_from_package(self):
        """ExportJobRecord must be exported from models package."""
        models_init = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "infrastructure" / "models" / "__init__.py"
        )
        source = models_init.read_text()
        assert "ExportJobRecord" in source

    def test_to_dict_has_required_fields(self):
        """to_dict() must include all required fields."""
        record = ExportJobRecord()
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


# ---------------------------------------------------------------------------
# REQ-4: Failed exports in DLQ
# ---------------------------------------------------------------------------
class TestDLQIntegration:
    """Failed exports must be written to DLQ."""

    def test_task_imports_dead_letter_queue(self):
        """Export task must import DLQ for failure recording."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "dead_letter_queue" in source

    def test_task_calls_record_failure_on_max_retries(self):
        """Task must call record_failure when max retries exceeded."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "record_failure" in source
        assert "MaxRetriesExceededError" in source

    def test_task_marks_job_failed(self):
        """Task must mark job as failed in DB on permanent failure."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "_mark_job_failed" in source
        assert '"failed"' in source


# ---------------------------------------------------------------------------
# REQ-5: Idempotent re-triggering
# ---------------------------------------------------------------------------
class TestIdempotency:
    """Re-triggering same export job must be idempotent."""

    def test_task_checks_job_status_before_processing(self):
        """Task must check if job is already completed/processing."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "idempotent" in source.lower()
        assert '"completed"' in source
        assert '"processing"' in source

    def test_task_skips_completed_jobs(self):
        """Task must skip jobs already in completed state."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        # Check for the idempotency guard
        assert 'job.status in ("completed", "processing")' in source

    def test_task_logs_skip(self):
        """Task must log when skipping idempotent re-trigger."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "skipping" in source.lower()


# ---------------------------------------------------------------------------
# Export format support
# ---------------------------------------------------------------------------
class TestExportFormats:
    """All required export formats must be supported."""

    def test_excel_generator_exists(self):
        """Excel export generator function must exist."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "_generate_excel" in source

    def test_csv_generator_exists(self):
        """CSV export generator function must exist."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "_generate_csv" in source

    def test_json_generator_exists(self):
        """JSON export generator function must exist."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "_generate_json" in source

    def test_markdown_generator_exists(self):
        """Markdown export generator function must exist."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "_generate_markdown" in source

    def test_llm_generator_exists(self):
        """LLM report generator function must exist."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "_generate_llm_report" in source

    def test_unsupported_format_raises(self):
        """Unsupported format must raise ValueError."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "Unsupported export format" in source


# ---------------------------------------------------------------------------
# Celery configuration
# ---------------------------------------------------------------------------
class TestCeleryConfiguration:
    """Celery must be configured for async exports."""

    def test_export_queue_routing(self):
        """Export task must be routed to export queue in config."""
        config_path = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "celery_config.py"
        )
        source = config_path.read_text()
        assert "export" in source
        assert "task_routes" in source

    def test_time_limit_annotation(self):
        """Export task must have time limit annotations."""
        config_path = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "celery_config.py"
        )
        source = config_path.read_text()
        assert "task_annotations" in source
        assert "150" in source  # hard limit
        assert "120" in source  # soft limit

    def test_story_111_comment(self):
        """Celery config must reference STORY-111."""
        config_path = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "celery_config.py"
        )
        source = config_path.read_text()
        assert "STORY-111" in source


# ---------------------------------------------------------------------------
# API wiring
# ---------------------------------------------------------------------------
class TestAPIWiring:
    """Export API must be wired into the FastAPI application."""

    def test_exports_router_in_main(self):
        """main.py must include the exports router."""
        main_path = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "api" / "main.py"
        )
        source = main_path.read_text()
        assert "exports_router" in source or "exports" in source

    def test_story_111_documented_in_main(self):
        """main.py must reference STORY-111."""
        main_path = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "api" / "main.py"
        )
        source = main_path.read_text()
        assert "STORY-111" in source


# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------
class TestDocumentation:
    """Export API must be documented."""

    def test_api_documentation_exists(self):
        """Export API documentation must exist."""
        doc_path = (
            Path(__file__).parent.parent.parent
            / "docs" / "exports" / "async-export-api.md"
        )
        assert doc_path.exists()

    def test_documentation_covers_endpoints(self):
        """Documentation must cover both POST and GET endpoints."""
        doc_path = (
            Path(__file__).parent.parent.parent
            / "docs" / "exports" / "async-export-api.md"
        )
        source = doc_path.read_text()
        assert "POST" in source
        assert "GET" in source
        assert "/api/v1/exports" in source
        assert "202" in source

    def test_documentation_covers_schema(self):
        """Documentation must describe the export_jobs table."""
        doc_path = (
            Path(__file__).parent.parent.parent
            / "docs" / "exports" / "async-export-api.md"
        )
        source = doc_path.read_text()
        assert "export_jobs" in source
        assert "tenant_id" in source
        assert "file_url" in source

    def test_task_module_has_docstring(self):
        """export_tasks.py must have a module docstring."""
        source = Path(_EXPORT_TASKS_PATH).read_text()
        assert "STORY-111" in source
        assert '"""' in source

    def test_model_module_has_docstring(self):
        """export.py model must have a module docstring."""
        model_path = (
            Path(__file__).parent.parent.parent
            / "src" / "solstein" / "infrastructure" / "models" / "export.py"
        )
        source = model_path.read_text()
        assert "STORY-111" in source
        assert "append" in source.lower()
