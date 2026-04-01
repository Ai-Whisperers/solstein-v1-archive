"""Tests for STORY-097: Automate Alembic Migrations Pre-Deploy.

Validates the migration runner script, workflow integration, Makefile
targets, and rollback documentation.
"""

import importlib.util
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_migration_module() -> ModuleType:
    """Load the migration runner script as a module for testing."""
    spec = importlib.util.spec_from_file_location(
        "run_migrations",
        str(PROJECT_ROOT / "scripts" / "ci" / "run_migrations.py"),
    )
    assert spec is not None, "Could not find run_migrations.py"
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class TestMigrationRunnerScript:
    """Verify the migration runner script exists and has required features."""

    def test_script_exists(self):
        """Migration runner script must exist."""
        path = PROJECT_ROOT / "scripts" / "ci" / "run_migrations.py"
        assert path.exists(), f"run_migrations.py not found at {path}"

    def test_script_has_timeout_support(self):
        """Script must support --timeout argument."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "run_migrations.py").read_text()
        assert "--timeout" in content

    def test_script_has_dry_run_support(self):
        """Script must support --dry-run argument."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "run_migrations.py").read_text()
        assert "--dry-run" in content

    def test_script_calls_alembic_upgrade_head(self):
        """Script must invoke alembic upgrade head."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "run_migrations.py").read_text()
        assert "alembic" in content
        assert "upgrade" in content
        assert "head" in content

    def test_script_has_structured_logging(self):
        """Script must emit structured logs with revision and duration."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "run_migrations.py").read_text()
        assert "duration" in content.lower() or "Duration" in content
        assert "revision" in content.lower() or "Revision" in content

    def test_script_handles_timeout(self):
        """Script must handle migration timeout gracefully."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "run_migrations.py").read_text()
        assert "MigrationTimeoutError" in content or "TimeoutExpired" in content

    def test_script_is_idempotent(self):
        """Script must be a no-op when database is already at head."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "run_migrations.py").read_text()
        assert "no-op" in content.lower() or "already at head" in content.lower()

    def test_script_returns_nonzero_on_failure(self):
        """Script must return non-zero exit code on failure."""
        content = (PROJECT_ROOT / "scripts" / "ci" / "run_migrations.py").read_text()
        assert "return 1" in content


class TestMigrationRunnerLogic:
    """Test the migration runner functions directly."""

    def test_run_migration_returns_zero_on_no_op(self):
        """When current == head, run_migration returns 0 (no-op)."""
        mod = _load_migration_module()

        with (
            patch.object(mod, "get_current_revision", return_value="abc123"),
            patch.object(mod, "get_head_revision", return_value="abc123"),
        ):
            result = mod.run_migration(timeout_seconds=10)
            assert result == 0

    def test_run_migration_dry_run_returns_zero(self):
        """Dry run returns 0 without applying."""
        mod = _load_migration_module()

        with (
            patch.object(mod, "get_current_revision", return_value="abc123"),
            patch.object(mod, "get_head_revision", return_value="def456"),
        ):
            result = mod.run_migration(timeout_seconds=10, dry_run=True)
            assert result == 0

    def test_run_migration_returns_one_on_failure(self):
        """Migration subprocess failure returns 1."""
        mod = _load_migration_module()

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "error output"
        mock_result.stderr = "error details"

        with (
            patch.object(mod, "get_current_revision", return_value="abc123"),
            patch.object(mod, "get_head_revision", return_value="def456"),
            patch("subprocess.run", return_value=mock_result),
        ):
            result = mod.run_migration(timeout_seconds=10)
            assert result == 1


class TestDeployStagingWorkflow:
    """Verify deploy-staging.yml has migration step before deploy."""

    @pytest.fixture
    def staging_workflow(self):
        path = PROJECT_ROOT / ".github" / "workflows" / "deploy-staging.yml"
        assert path.exists()
        with open(path) as f:
            return yaml.safe_load(f)

    def test_migrate_job_exists(self, staging_workflow):
        """Staging workflow must have a migrate job."""
        assert "migrate" in staging_workflow["jobs"]

    def test_deploy_depends_on_migrate(self, staging_workflow):
        """Deploy job must depend on migrate job."""
        deploy = staging_workflow["jobs"]["deploy"]
        needs = deploy.get("needs", [])
        if isinstance(needs, str):
            needs = [needs]
        assert "migrate" in needs, "Deploy must depend on migrate"

    def test_migrate_runs_migration_script(self, staging_workflow):
        """Migrate job must run the migration script."""
        migrate = staging_workflow["jobs"]["migrate"]
        steps = migrate.get("steps", [])
        step_runs = " ".join(str(s.get("run", "")) for s in steps)
        assert "run_migrations.py" in step_runs

    def test_migrate_uses_database_secret(self, staging_workflow):
        """Migrate job must use DATABASE__URL from secrets."""
        migrate = staging_workflow["jobs"]["migrate"]
        steps = migrate.get("steps", [])
        all_env = " ".join(str(s.get("env", "")) for s in steps)
        assert "DATABASE__URL" in all_env or "STAGING_DATABASE_URL" in all_env


class TestDeployProductionWorkflow:
    """Verify deploy-production.yml has migration step before deploy.

    Note: The production workflow contains a JavaScript template literal with
    brackets that confuses PyYAML safe_load, so we use text-based checks
    instead of YAML parsing.
    """

    @pytest.fixture
    def prod_workflow_text(self) -> str:
        path = PROJECT_ROOT / ".github" / "workflows" / "deploy-production.yml"
        assert path.exists()
        return path.read_text()

    def test_migrate_job_exists(self, prod_workflow_text: str) -> None:
        """Production workflow must have a migrate-production job."""
        assert "migrate-production:" in prod_workflow_text

    def test_deploy_depends_on_migrate(self, prod_workflow_text: str) -> None:
        """Deploy job must depend on migrate-production job."""
        assert "migrate-production" in prod_workflow_text
        # The needs line should list migrate-production
        assert "needs: [pre-deployment-checks, migrate-production]" in prod_workflow_text


class TestMakefileTargets:
    """Verify Makefile has migration targets."""

    @pytest.fixture
    def makefile_content(self):
        path = PROJECT_ROOT / "Makefile"
        assert path.exists()
        return path.read_text()

    def test_migrate_target_exists(self, makefile_content):
        """Makefile must have a migrate target."""
        assert "migrate:" in makefile_content

    def test_migrate_dry_run_target_exists(self, makefile_content):
        """Makefile must have a migrate-dry-run target."""
        assert "migrate-dry-run:" in makefile_content

    def test_migrate_rollback_target_exists(self, makefile_content):
        """Makefile must have a migrate-rollback target."""
        assert "migrate-rollback:" in makefile_content

    def test_migrate_status_target_exists(self, makefile_content):
        """Makefile must have a migrate-status target."""
        assert "migrate-status:" in makefile_content


class TestRollbackRunbook:
    """Verify rollback documentation exists."""

    def test_runbook_exists(self):
        """Migration rollback runbook must exist."""
        path = PROJECT_ROOT / "docs" / "runbooks" / "migration-rollback.md"
        assert path.exists()

    def test_runbook_has_rollback_command(self):
        """Runbook must document the rollback command."""
        path = PROJECT_ROOT / "docs" / "runbooks" / "migration-rollback.md"
        content = path.read_text()
        assert "alembic downgrade" in content

    def test_runbook_has_verification_step(self):
        """Runbook must include verification after rollback."""
        path = PROJECT_ROOT / "docs" / "runbooks" / "migration-rollback.md"
        content = path.read_text()
        assert "verify" in content.lower() or "Verify" in content
