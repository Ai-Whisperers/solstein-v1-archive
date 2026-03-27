"""Tests for STORY-098: Add migrate, seed, deploy Makefile Targets.

Validates that the Makefile has all required targets with correct
implementations for migration, seeding, deployment, and help.
"""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def makefile_content() -> str:
    """Load the Makefile content."""
    path = PROJECT_ROOT / "Makefile"
    assert path.exists(), "Makefile not found"
    return path.read_text()


class TestMigrateDownTarget:
    """Verify migrate-down target with confirmation prompt."""

    def test_migrate_down_target_exists(self, makefile_content: str) -> None:
        """Makefile must have a migrate-down target."""
        assert "migrate-down:" in makefile_content

    def test_migrate_down_has_confirmation(self, makefile_content: str) -> None:
        """migrate-down must prompt for confirmation."""
        assert "CONFIRM" in makefile_content
        assert "yes" in makefile_content

    def test_migrate_down_calls_alembic_downgrade(self, makefile_content: str) -> None:
        """migrate-down must call alembic downgrade."""
        # Find the migrate-down section
        lines = makefile_content.split("\n")
        in_target = False
        found_downgrade = False
        for line in lines:
            if line.startswith("migrate-down:"):
                in_target = True
                continue
            if in_target:
                if line and not line.startswith("\t") and not line.startswith("#"):
                    break
                if "alembic downgrade" in line:
                    found_downgrade = True
        assert found_downgrade, "migrate-down must call alembic downgrade"

    def test_migrate_down_is_phony(self, makefile_content: str) -> None:
        """migrate-down must be declared as .PHONY."""
        phony_line = [line for line in makefile_content.split("\n") if line.startswith(".PHONY:")][0]
        assert "migrate-down" in phony_line


class TestCheckMigrationsTarget:
    """Verify check-migrations target for CI gating."""

    def test_target_exists(self, makefile_content: str) -> None:
        """Makefile must have a check-migrations target."""
        assert "check-migrations:" in makefile_content

    def test_checks_current_vs_head(self, makefile_content: str) -> None:
        """check-migrations must compare current revision to head."""
        assert "alembic" in makefile_content
        assert "current" in makefile_content
        assert "heads" in makefile_content

    def test_exits_nonzero_on_pending(self, makefile_content: str) -> None:
        """check-migrations must exit non-zero if migrations are pending."""
        # The target should contain sys.exit(1) for pending state
        assert "sys.exit(1)" in makefile_content

    def test_is_phony(self, makefile_content: str) -> None:
        """check-migrations must be declared as .PHONY."""
        phony_line = [line for line in makefile_content.split("\n") if line.startswith(".PHONY:")][0]
        assert "check-migrations" in phony_line


class TestSeedTargets:
    """Verify seed and seed-test targets."""

    def test_seed_target_exists(self, makefile_content: str) -> None:
        """Makefile must have a seed target."""
        assert "\nseed:" in makefile_content or makefile_content.startswith("seed:")

    def test_seed_calls_seed_script(self, makefile_content: str) -> None:
        """seed target must call seed_db.py."""
        assert "seed_db.py" in makefile_content

    def test_seed_test_target_exists(self, makefile_content: str) -> None:
        """Makefile must have a seed-test target."""
        assert "seed-test:" in makefile_content

    def test_seed_test_uses_test_database(self, makefile_content: str) -> None:
        """seed-test must use TEST_DATABASE_URL."""
        # Find the seed-test section and check it references test DB
        lines = makefile_content.split("\n")
        in_target = False
        found_test_db = False
        for line in lines:
            if line.startswith("seed-test:"):
                in_target = True
                continue
            if in_target:
                if line and not line.startswith("\t") and not line.startswith("#"):
                    break
                if "TEST_DATABASE_URL" in line:
                    found_test_db = True
        assert found_test_db, "seed-test must use TEST_DATABASE_URL"

    def test_seed_targets_are_phony(self, makefile_content: str) -> None:
        """seed and seed-test must be declared as .PHONY."""
        phony_line = [line for line in makefile_content.split("\n") if line.startswith(".PHONY:")][0]
        assert "seed" in phony_line
        assert "seed-test" in phony_line


class TestDeployTarget:
    """Verify deploy readiness target."""

    def test_deploy_target_exists(self, makefile_content: str) -> None:
        """Makefile must have a deploy target."""
        assert "\ndeploy:" in makefile_content or makefile_content.startswith("deploy:")

    def test_deploy_runs_lint(self, makefile_content: str) -> None:
        """deploy must run linting."""
        lines = makefile_content.split("\n")
        in_target = False
        found_lint = False
        for line in lines:
            if line.startswith("deploy:"):
                in_target = True
                continue
            if in_target:
                if line and not line.startswith("\t") and not line.startswith("#") and not line.startswith("@"):
                    break
                if "lint" in line:
                    found_lint = True
        assert found_lint, "deploy must run lint checks"

    def test_deploy_runs_tests(self, makefile_content: str) -> None:
        """deploy must run tests."""
        lines = makefile_content.split("\n")
        in_target = False
        found_test = False
        for line in lines:
            if line.startswith("deploy:"):
                in_target = True
                continue
            if in_target:
                if line and not line.startswith("\t") and not line.startswith("#") and not line.startswith("@"):
                    break
                if "pytest" in line:
                    found_test = True
        assert found_test, "deploy must run tests"

    def test_deploy_checks_migrations(self, makefile_content: str) -> None:
        """deploy must check migrations."""
        lines = makefile_content.split("\n")
        in_target = False
        found_migrate = False
        for line in lines:
            if line.startswith("deploy:"):
                in_target = True
                continue
            if in_target:
                if line and not line.startswith("\t") and not line.startswith("#") and not line.startswith("@"):
                    break
                if "check-migrations" in line:
                    found_migrate = True
        assert found_migrate, "deploy must check migrations"

    def test_deploy_is_phony(self, makefile_content: str) -> None:
        """deploy must be declared as .PHONY."""
        phony_line = [line for line in makefile_content.split("\n") if line.startswith(".PHONY:")][0]
        assert "deploy" in phony_line


class TestHelpTarget:
    """Verify help target lists all key commands."""

    def test_help_target_exists(self, makefile_content: str) -> None:
        """Makefile must have a help target."""
        assert "\nhelp:" in makefile_content or makefile_content.startswith("help:")

    def test_help_lists_migrate(self, makefile_content: str) -> None:
        """help must list migrate target."""
        assert "make migrate" in makefile_content

    def test_help_lists_seed(self, makefile_content: str) -> None:
        """help must list seed target."""
        assert "make seed" in makefile_content

    def test_help_lists_deploy(self, makefile_content: str) -> None:
        """help must list deploy target."""
        assert "make deploy" in makefile_content

    def test_help_lists_check_migrations(self, makefile_content: str) -> None:
        """help must list check-migrations target."""
        assert "make check-migrations" in makefile_content

    def test_help_is_phony(self, makefile_content: str) -> None:
        """help must be declared as .PHONY."""
        phony_line = [line for line in makefile_content.split("\n") if line.startswith(".PHONY:")][0]
        assert "help" in phony_line


class TestSeedScriptExists:
    """Verify the seed script referenced by Makefile exists."""

    def test_seed_script_exists(self) -> None:
        """scripts/seed_db.py must exist."""
        path = PROJECT_ROOT / "scripts" / "seed_db.py"
        assert path.exists(), f"seed_db.py not found at {path}"

    def test_seed_script_has_count_arg(self) -> None:
        """seed_db.py must support --count argument."""
        content = (PROJECT_ROOT / "scripts" / "seed_db.py").read_text()
        assert "--count" in content
