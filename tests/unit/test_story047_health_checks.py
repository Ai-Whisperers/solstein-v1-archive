"""Tests for STORY-047: Replace Fake Health Checks with Real Infrastructure Probes.

.. deprecated:: STORY-253
   The source-inspection tests in this file (84.8% of assertions read source
   with ``Path.read_text()``) have been superseded by behavioral contract
   tests in ``test_behavioral_contracts.py`` which verify route registration,
   health check class existence, strategy inheritance, and HealthCheckResult
   fields at runtime.

   This file is retained for backward-compatibility during the transition.
   New health-check contract tests should go in ``test_behavioral_contracts.py``.

Validates that health check endpoints use real probes and return per-component status.
"""

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC = PROJECT_ROOT / "src" / "solstein"
HEALTH_ROUTER = SRC / "api" / "routers" / "health.py"
CORE_MONITORING = SRC / "core" / "monitoring.py"
HEALTH_CHECKS_DIR = SRC / "core" / "health_checks"
DB_CHECK = HEALTH_CHECKS_DIR / "database.py"
REDIS_CHECK = HEALTH_CHECKS_DIR / "redis.py"
LLM_CHECK = HEALTH_CHECKS_DIR / "llm.py"
API_CHECK = HEALTH_CHECKS_DIR / "api.py"
CONFIG_CHECK = HEALTH_CHECKS_DIR / "configuration.py"
MONITORING_HEALTH = SRC / "monitoring" / "health.py"
DOCS_HEALTH = PROJECT_ROOT / "docs" / "runbooks" / "health-endpoints.md"


# ===========================================================================
# REQ-6: No asyncio.sleep in health check logic
# ===========================================================================


class TestNoAsyncioSleep:
    """STORY-047 REQ-6: asyncio.sleep must not appear in health check logic."""

    def test_no_sleep_in_core_monitoring(self):
        text = CORE_MONITORING.read_text()
        assert "asyncio.sleep" not in text, "asyncio.sleep found in core/monitoring.py"

    def test_no_sleep_in_database_check(self):
        text = DB_CHECK.read_text()
        assert "asyncio.sleep" not in text, "asyncio.sleep found in database health check"

    def test_no_sleep_in_redis_check(self):
        text = REDIS_CHECK.read_text()
        assert "asyncio.sleep" not in text, "asyncio.sleep found in redis health check"

    def test_no_sleep_in_llm_check(self):
        text = LLM_CHECK.read_text()
        assert "asyncio.sleep" not in text, "asyncio.sleep found in llm health check"

    def test_no_sleep_in_api_check(self):
        text = API_CHECK.read_text()
        assert "asyncio.sleep" not in text, "asyncio.sleep found in api health check"

    def test_no_sleep_in_config_check(self):
        text = CONFIG_CHECK.read_text()
        assert "asyncio.sleep" not in text, "asyncio.sleep found in config health check"

    def test_no_sleep_in_health_router(self):
        text = HEALTH_ROUTER.read_text()
        assert "asyncio.sleep" not in text, "asyncio.sleep found in health router"


# ===========================================================================
# REQ-1: Database probe does SELECT 1
# ===========================================================================


class TestDatabaseProbe:
    """STORY-047 REQ-1: Health endpoint must attempt real database connection."""

    def test_database_check_uses_select_1(self):
        text = DB_CHECK.read_text()
        assert "SELECT 1" in text, "Database health check must use SELECT 1"

    def test_database_check_uses_sqlalchemy(self):
        text = DB_CHECK.read_text()
        assert "sqlalchemy" in text, "Database check should use sqlalchemy"

    def test_database_check_returns_unhealthy_on_failure(self):
        text = DB_CHECK.read_text()
        assert "UNHEALTHY" in text, "Database check must return UNHEALTHY on failure"


# ===========================================================================
# REQ-2: Redis probe does real ping
# ===========================================================================


class TestRedisProbe:
    """STORY-047 REQ-2: Health endpoint must attempt real Redis ping."""

    def test_redis_check_uses_ping(self):
        text = REDIS_CHECK.read_text()
        assert ".ping()" in text, "Redis health check must call ping()"

    def test_redis_check_uses_redis_asyncio(self):
        text = REDIS_CHECK.read_text()
        assert "redis.asyncio" in text, "Redis check should use redis.asyncio"

    def test_redis_check_returns_unhealthy_on_failure(self):
        """STORY-047: Redis failure should report unhealthy (not degraded)."""
        text = REDIS_CHECK.read_text()
        # The except block should set UNHEALTHY status
        assert "HealthStatus.UNHEALTHY" in text


# ===========================================================================
# REQ-3: LLM provider reachability
# ===========================================================================


class TestLLMProbe:
    """STORY-047 REQ-3: Health endpoint must check LLM provider reachability."""

    def test_llm_check_calls_provider_health(self):
        text = LLM_CHECK.read_text()
        assert "check_all_providers" in text, "LLM check should call check_all_providers"

    def test_llm_check_reports_available_providers(self):
        text = LLM_CHECK.read_text()
        assert "available_providers" in text


# ===========================================================================
# REQ-4: Per-component status in /health response
# ===========================================================================


class TestPerComponentStatus:
    """STORY-047 REQ-4: Response must include per-component status."""

    def test_health_endpoint_returns_components(self):
        """The /health endpoint must include a 'components' dict."""
        text = HEALTH_ROUTER.read_text()
        assert '"components"' in text or "'components'" in text, "Health endpoint must return components dict"

    def test_health_endpoint_maps_component_status(self):
        """Components dict should map name -> status string."""
        text = HEALTH_ROUTER.read_text()
        assert "check.status" in text, "Should map check names to their status"

    def test_readiness_endpoint_includes_components(self):
        """The /health/ready endpoint should also include components."""
        text = HEALTH_ROUTER.read_text()
        # Find the readiness_check function and verify it has components
        idx = text.find("readiness_check")
        after = text[idx:]
        assert "components" in after, "Readiness check should include components"


# ===========================================================================
# REQ-5: Probe failures don't crash the endpoint
# ===========================================================================


class TestProbeFailureResilience:
    """STORY-047 REQ-5: Probe failures must not crash the health endpoint."""

    def test_database_check_has_exception_handler(self):
        text = DB_CHECK.read_text()
        assert "except Exception" in text

    def test_redis_check_has_exception_handler(self):
        text = REDIS_CHECK.read_text()
        assert "except Exception" in text

    def test_llm_check_has_exception_handler(self):
        text = LLM_CHECK.read_text()
        assert "except Exception" in text

    def test_api_check_has_exception_handler(self):
        text = API_CHECK.read_text()
        assert "except Exception" in text

    def test_config_check_has_exception_handler(self):
        text = CONFIG_CHECK.read_text()
        assert "except Exception" in text


# ===========================================================================
# Critical component logic
# ===========================================================================


class TestCriticalComponentLogic:
    """STORY-047: Overall status depends on component criticality."""

    def test_health_monitor_defines_critical_components(self):
        text = CORE_MONITORING.read_text()
        assert "CRITICAL_COMPONENTS" in text, "Must define CRITICAL_COMPONENTS set"

    def test_database_is_critical(self):
        text = CORE_MONITORING.read_text()
        assert '"database"' in text or "'database'" in text

    def test_configuration_is_critical(self):
        text = CORE_MONITORING.read_text()
        assert '"configuration"' in text or "'configuration'" in text

    def test_redis_not_critical(self):
        """Redis failure should result in degraded, not unhealthy overall."""
        text = CORE_MONITORING.read_text()
        # Verify redis is NOT in CRITICAL_COMPONENTS
        match = re.search(r"CRITICAL_COMPONENTS\s*=\s*\{([^}]+)\}", text)
        assert match, "Could not find CRITICAL_COMPONENTS definition"
        critical = match.group(1)
        assert "redis" not in critical, "Redis should not be a critical component"

    def test_overall_status_degraded_for_noncritical_failure(self):
        """Non-critical unhealthy -> overall degraded (not unhealthy)."""
        text = CORE_MONITORING.read_text()
        # The get_overall_status method should check critical first, then degrade
        assert "DEGRADED" in text


# ===========================================================================
# Documentation
# ===========================================================================


class TestDocumentation:
    """STORY-047: Health endpoint schema must be documented."""

    def test_health_endpoints_doc_exists(self):
        assert DOCS_HEALTH.exists(), "docs/runbooks/health-endpoints.md must exist"

    def test_doc_covers_health_endpoint(self):
        text = DOCS_HEALTH.read_text()
        assert "/health" in text

    def test_doc_covers_component_status(self):
        text = DOCS_HEALTH.read_text()
        assert "components" in text

    def test_doc_covers_criticality(self):
        text = DOCS_HEALTH.read_text()
        assert "Critical" in text

    def test_doc_covers_probe_timeouts(self):
        text = DOCS_HEALTH.read_text()
        assert "Timeout" in text or "timeout" in text

    def test_doc_covers_readiness(self):
        text = DOCS_HEALTH.read_text()
        assert "/health/ready" in text

    def test_doc_covers_liveness(self):
        text = DOCS_HEALTH.read_text()
        assert "/health/live" in text


# ===========================================================================
# Monitoring health module (src/solstein/monitoring/health.py)
# ===========================================================================


class TestMonitoringHealthModule:
    """Verify monitoring/health.py also uses real probes."""

    def test_monitoring_health_check_database_uses_select(self):
        text = MONITORING_HEALTH.read_text()
        assert "SELECT 1" in text

    def test_monitoring_health_check_redis_uses_ping(self):
        text = MONITORING_HEALTH.read_text()
        assert ".ping()" in text

    def test_monitoring_health_no_asyncio_sleep(self):
        text = MONITORING_HEALTH.read_text()
        assert "asyncio.sleep" not in text
