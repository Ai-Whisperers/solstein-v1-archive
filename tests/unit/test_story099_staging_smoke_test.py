"""Tests for STORY-099: Add Staging Deploy + Post-Deploy Smoke Test Workflow.

Validates the smoke test script exists and the staging/production workflows
include proper smoke tests, rollback, and notifications.
"""

import os
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestSmokeTestScript:
    """Verify the smoke test script exists and has required features."""

    def test_script_exists(self) -> None:
        """Smoke test script must exist."""
        path = PROJECT_ROOT / "scripts" / "ci" / "smoke_test.sh"
        assert path.exists(), f"smoke_test.sh not found at {path}"

    def test_script_is_executable(self) -> None:
        """Smoke test script must be executable."""
        path = PROJECT_ROOT / "scripts" / "ci" / "smoke_test.sh"
        assert os.access(path, os.X_OK), "smoke_test.sh must be executable"

    def test_script_checks_health_endpoint(self) -> None:
        """Script must check the health endpoint."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "smoke_test.sh").read_text()
        assert "/health" in content

    def test_script_checks_api_endpoint(self) -> None:
        """Script must check an API endpoint."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "smoke_test.sh").read_text()
        assert "/api/v1/" in content

    def test_script_validates_json(self) -> None:
        """Script must validate JSON responses."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "smoke_test.sh").read_text()
        assert "json" in content.lower()

    def test_script_accepts_base_url(self) -> None:
        """Script must accept a base URL argument."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "smoke_test.sh").read_text()
        assert "BASE_URL" in content

    def test_script_exits_nonzero_on_failure(self) -> None:
        """Script must exit non-zero on test failure."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "smoke_test.sh").read_text()
        assert "exit 1" in content

    def test_script_reports_results(self) -> None:
        """Script must report pass/fail counts."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "smoke_test.sh").read_text()
        assert "PASS" in content
        assert "FAIL" in content


class TestStagingWorkflowSmokeTests:
    """Verify staging workflow has proper smoke tests and rollback."""

    @pytest.fixture
    def staging_workflow(self) -> dict:
        path = PROJECT_ROOT / ".github" / "workflows" / "deploy-staging.yml"
        assert path.exists()
        with open(path) as f:
            return yaml.safe_load(f)

    def test_deploy_job_runs_smoke_tests(self, staging_workflow: dict) -> None:
        """Deploy job must run smoke_test.sh."""
        deploy = staging_workflow["jobs"]["deploy"]
        steps = deploy.get("steps", [])
        step_runs = " ".join(str(s.get("run", "")) for s in steps)
        assert "smoke_test.sh" in step_runs

    def test_rollback_job_exists(self, staging_workflow: dict) -> None:
        """Staging workflow must have a rollback-on-failure job."""
        assert "rollback-on-failure" in staging_workflow["jobs"]

    def test_rollback_runs_on_failure(self, staging_workflow: dict) -> None:
        """Rollback job must only run on failure."""
        rollback = staging_workflow["jobs"]["rollback-on-failure"]
        assert "failure()" in str(rollback.get("if", ""))

    def test_notify_job_exists(self, staging_workflow: dict) -> None:
        """Staging workflow must have a notify job."""
        assert "notify" in staging_workflow["jobs"]

    def test_notify_runs_always(self, staging_workflow: dict) -> None:
        """Notify job must run always (success or failure)."""
        notify = staging_workflow["jobs"]["notify"]
        assert "always()" in str(notify.get("if", ""))

    def test_deploy_waits_for_stabilization(self, staging_workflow: dict) -> None:
        """Deploy must wait for service to stabilize before smoke tests."""
        deploy = staging_workflow["jobs"]["deploy"]
        steps = deploy.get("steps", [])
        step_runs = " ".join(str(s.get("run", "")) + str(s.get("name", "")) for s in steps)
        assert "stabilize" in step_runs.lower() or "sleep" in step_runs


class TestProductionWorkflowGating:
    """Verify production workflow gates on staging success.

    Note: The production workflow contains a JavaScript template literal that
    confuses PyYAML safe_load, so we use text-based checks.
    """

    @pytest.fixture
    def prod_workflow_text(self) -> str:
        path = PROJECT_ROOT / ".github" / "workflows" / "deploy-production.yml"
        assert path.exists()
        return path.read_text()

    def test_production_verifies_staging(self, prod_workflow_text: str) -> None:
        """Production workflow must verify staging deployment succeeded."""
        assert "staging" in prod_workflow_text.lower()
        assert "deploy-staging" in prod_workflow_text

    def test_production_uses_smoke_test_script(self, prod_workflow_text: str) -> None:
        """Production workflow must use the smoke test script."""
        assert "smoke_test.sh" in prod_workflow_text

    def test_production_checks_staging_conclusion(self, prod_workflow_text: str) -> None:
        """Production must check staging workflow conclusion."""
        assert "conclusion" in prod_workflow_text or "STAGING_STATUS" in prod_workflow_text

    def test_production_blocks_on_staging_failure(self, prod_workflow_text: str) -> None:
        """Production must block deploy if staging didn't succeed."""
        assert "exit 1" in prod_workflow_text
