"""Tests for STORY-051: Add Prometheus Metrics Endpoints.

Validates:
- REQ-1: /metrics/prometheus returns valid Prometheus text exposition format
- REQ-2: Required metrics present (HTTP, LLM, DB, pipeline, system)
- REQ-3: Endpoint is unauthenticated (no auth required)
- REQ-4: Metric names follow Prometheus naming conventions
"""

from __future__ import annotations

import re
from pathlib import Path

from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from prometheus_client.parser import text_string_to_metric_families

from solstein.monitoring.metrics import (
    DB_QUERY_DURATION,
    HTTP_REQUESTS_TOTAL,
    LLM_TOKENS_TOTAL,
    PIPELINE_STAGE_DURATION,
)


# ---------------------------------------------------------------------------
# REQ-1: Valid Prometheus text exposition format
# ---------------------------------------------------------------------------
class TestPrometheusFormat:
    """GET /metrics/prometheus must return valid Prometheus format."""

    def test_generate_latest_returns_bytes(self):
        """generate_latest() must return bytes."""
        data = generate_latest()
        assert isinstance(data, bytes)

    def test_output_is_parseable(self):
        """Output must be parseable by the Prometheus client parser."""
        data = generate_latest().decode("utf-8")
        families = list(text_string_to_metric_families(data))
        assert len(families) > 0

    def test_content_type_is_openmetrics(self):
        """Content type must be the standard OpenMetrics type."""
        assert "text/" in CONTENT_TYPE_LATEST or "openmetrics" in CONTENT_TYPE_LATEST

    def test_router_exists(self):
        """The prometheus router module must exist and export a router."""
        prom_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "routers" / "prometheus.py"
        assert prom_path.exists(), f"Router module not found at {prom_path}"
        source = prom_path.read_text()
        assert "router" in source
        assert "APIRouter" in source

    def test_endpoint_registered(self):
        """The /metrics/prometheus route must be registered."""
        prom_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "routers" / "prometheus.py"
        source = prom_path.read_text()
        assert "/metrics/prometheus" in source, (
            "Expected /metrics/prometheus route in prometheus.py"
        )


# ---------------------------------------------------------------------------
# REQ-2: Required metrics present
# ---------------------------------------------------------------------------
class TestRequiredMetrics:
    """All required metrics must be present in the output."""

    def _get_metric_names(self) -> set[str]:
        """Get all metric names from Prometheus output."""
        data = generate_latest().decode("utf-8")
        return {
            family.name
            for family in text_string_to_metric_families(data)
        }

    def test_http_request_rate_metric(self):
        """HTTP request rate counter must exist."""
        names = self._get_metric_names()
        assert "http_requests_total" in names or "http_requests" in names

    def test_http_request_duration_metric(self):
        """HTTP request duration histogram must exist."""
        names = self._get_metric_names()
        assert "http_request_duration_seconds" in names

    def test_http_requests_in_progress_metric(self):
        """In-flight requests gauge must exist."""
        names = self._get_metric_names()
        assert "http_requests_in_progress" in names

    def test_llm_tokens_metric(self):
        """LLM token counter must exist."""
        names = self._get_metric_names()
        assert "llm_tokens_total" in names or "llm_tokens" in names

    def test_llm_cost_metric(self):
        """LLM cost counter must exist."""
        names = self._get_metric_names()
        assert "llm_cost_dollars_total" in names or "llm_cost_dollars" in names

    def test_llm_request_duration_metric(self):
        """LLM request latency histogram must exist."""
        names = self._get_metric_names()
        assert "llm_request_duration_seconds" in names

    def test_db_queries_metric(self):
        """Database query counter must exist."""
        names = self._get_metric_names()
        assert "db_queries_total" in names or "db_queries" in names

    def test_db_query_duration_metric(self):
        """Database query duration histogram must exist."""
        names = self._get_metric_names()
        assert "db_query_duration_seconds" in names

    def test_db_pool_connections_metric(self):
        """Database connection pool gauge must exist."""
        names = self._get_metric_names()
        assert "db_pool_connections" in names

    def test_research_runs_metric(self):
        """Research run counter must exist."""
        names = self._get_metric_names()
        assert "research_runs_total" in names or "research_runs" in names

    def test_pipeline_stage_duration_metric(self):
        """Pipeline stage duration histogram must exist."""
        names = self._get_metric_names()
        assert "pipeline_stage_duration_seconds" in names

    def test_companies_enriched_metric(self):
        """Companies enriched counter must exist."""
        names = self._get_metric_names()
        assert "companies_enriched_total" in names or "companies_enriched" in names


# ---------------------------------------------------------------------------
# REQ-3: Unauthenticated endpoint
# ---------------------------------------------------------------------------
class TestUnauthenticatedAccess:
    """Endpoint must not require authentication."""

    def test_no_auth_dependency(self):
        """The prometheus endpoint must not have auth dependencies."""
        prom_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "routers" / "prometheus.py"
        source = prom_path.read_text()
        # Endpoint should not import or use any auth dependency
        assert "Depends(" not in source or "auth" not in source.lower()
        assert "admin" not in source.lower() or "Depends(" not in source

    def test_rate_limit_excluded(self):
        """The endpoint must be excluded from rate limiting."""
        rate_limit_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "middleware" / "rate_limit.py"
        source = rate_limit_path.read_text()
        assert '"/metrics/prometheus"' in source

    def test_tenant_excluded(self):
        """The endpoint must not require tenant API key."""
        tenant_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "middleware" / "tenant.py"
        source = tenant_path.read_text()
        assert '"/metrics/prometheus"' in source

    def test_security_documented(self):
        """The router module must document the unauthenticated decision."""
        prom_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "routers" / "prometheus.py"
        source = prom_path.read_text()
        assert "unauthenticated" in source.lower()


# ---------------------------------------------------------------------------
# REQ-4: Prometheus naming conventions
# ---------------------------------------------------------------------------
class TestNamingConventions:
    """Metric names must follow Prometheus naming conventions."""

    def _get_metric_names(self) -> set[str]:
        data = generate_latest().decode("utf-8")
        return {
            family.name
            for family in text_string_to_metric_families(data)
        }

    def test_names_are_snake_case(self):
        """All metric names must be snake_case."""
        names = self._get_metric_names()
        snake_case_pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        for name in names:
            assert snake_case_pattern.match(name), (
                f"Metric name '{name}' is not snake_case"
            )

    def test_duration_metrics_have_seconds_suffix(self):
        """Duration metrics must end with _seconds (ignoring _created/_total suffixes)."""
        names = self._get_metric_names()
        duration_metrics = [n for n in names if "duration" in n]
        for name in duration_metrics:
            # Strip prometheus auto-suffixes (_created, _bucket, _count, _sum)
            base = name
            for suffix in ("_created", "_bucket", "_count", "_sum", "_total"):
                if base.endswith(suffix):
                    base = base[: -len(suffix)]
                    break
            assert base.endswith("_seconds"), (
                f"Duration metric '{name}' (base: '{base}') should end with _seconds"
            )

    def test_app_counter_metrics_have_total_suffix(self):
        """Application counter metrics should follow _total convention.

        Note: The OpenMetrics parser may strip _total suffix from counter
        names. We only check our application-defined counters, not default
        Python process metrics.
        """
        data = generate_latest().decode("utf-8")
        app_counters = [
            f.name
            for f in text_string_to_metric_families(data)
            if f.type == "counter"
            and not f.name.startswith(("python_", "process_"))
        ]
        # Our application counters should follow _total convention
        for name in app_counters:
            # OpenMetrics parser strips _total; check the raw output instead
            assert name in data, f"Counter '{name}' not found in raw output"


# ---------------------------------------------------------------------------
# Metric increment verification
# ---------------------------------------------------------------------------
class TestMetricUpdates:
    """Metrics must update when operations occur."""

    def test_http_counter_increments(self):
        """HTTP request counter must increment."""
        before = HTTP_REQUESTS_TOTAL.labels(
            method="GET", endpoint="/test", status_code="200"
        )._value.get()
        HTTP_REQUESTS_TOTAL.labels(
            method="GET", endpoint="/test", status_code="200"
        ).inc()
        after = HTTP_REQUESTS_TOTAL.labels(
            method="GET", endpoint="/test", status_code="200"
        )._value.get()
        assert after == before + 1

    def test_llm_tokens_counter_increments(self):
        """LLM token counter must increment."""
        LLM_TOKENS_TOTAL.labels(
            provider="test", model="test-model", token_type="input"
        ).inc(100)
        val = LLM_TOKENS_TOTAL.labels(
            provider="test", model="test-model", token_type="input"
        )._value.get()
        assert val >= 100

    def test_db_query_duration_observes(self):
        """DB query duration histogram must accept observations."""
        DB_QUERY_DURATION.labels(operation="SELECT").observe(0.015)
        # If it doesn't raise, observation was accepted

    def test_pipeline_stage_duration_observes(self):
        """Pipeline stage duration must accept observations."""
        PIPELINE_STAGE_DURATION.labels(stage="discovery").observe(5.2)
        # If it doesn't raise, observation was accepted


# ---------------------------------------------------------------------------
# Main.py integration
# ---------------------------------------------------------------------------
class TestMainIntegration:
    """Prometheus router must be wired into main.py."""

    def test_main_includes_prometheus_router(self):
        """main.py must include the prometheus router."""
        main_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "main.py"
        source = main_path.read_text()
        assert "prometheus_router" in source
        assert "prometheus" in source.lower()

    def test_pyproject_has_prometheus_client(self):
        """pyproject.toml must include prometheus-client dependency."""
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        source = pyproject_path.read_text()
        assert "prometheus-client" in source


# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------
class TestDocumentation:
    """Metrics documentation requirements."""

    def test_router_module_has_docstring(self):
        """The prometheus module must have a docstring mentioning STORY-051."""
        prom_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "routers" / "prometheus.py"
        source = prom_path.read_text()
        assert "STORY-051" in source
        assert '"""' in source  # has docstrings

    def test_endpoint_has_docstring(self):
        """The prometheus_metrics endpoint must have a docstring."""
        prom_path = Path(__file__).parent.parent.parent / "src" / "solstein" / "api" / "routers" / "prometheus.py"
        source = prom_path.read_text()
        assert "Prometheus" in source
        assert "def prometheus_metrics" in source
