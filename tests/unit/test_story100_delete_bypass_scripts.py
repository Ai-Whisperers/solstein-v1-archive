"""Tests for STORY-100: Delete Root Bypass Scripts.

Validates that root-level bypass scripts are gone, the CI lint rule
exists, and the migration guide is in place.
"""

import importlib.util
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestRootScriptsDeleted:
    """Verify bypass scripts have been removed from project root."""

    def test_no_run_research_py(self) -> None:
        """run_research.py must not exist in project root."""
        assert not (PROJECT_ROOT / "run_research.py").exists()

    def test_no_run_market_pipeline_py(self) -> None:
        """run_market_pipeline.py must not exist in project root."""
        assert not (PROJECT_ROOT / "run_market_pipeline.py").exists()

    def test_no_run_star_py_in_root(self) -> None:
        """No run_*.py scripts in project root."""
        matches = list(PROJECT_ROOT.glob("run_*.py"))
        assert matches == [], f"Found bypass scripts in root: {matches}"

    def test_only_allowed_py_in_root(self) -> None:
        """Only config files (conftest.py, setup.py) are allowed in root."""
        allowed = {"conftest.py", "setup.py", "setup.cfg"}
        root_py = [p.name for p in PROJECT_ROOT.glob("*.py")]
        forbidden = [name for name in root_py if name not in allowed]
        assert forbidden == [], f"Forbidden .py files in root: {forbidden}"


class TestCILintRule:
    """Verify the CI lint rule for root scripts exists."""

    def test_check_script_exists(self) -> None:
        """scripts/ci/check_root_scripts.py must exist."""
        path = PROJECT_ROOT / "scripts" / "ci" / "check_root_scripts.py"
        assert path.exists()

    def test_check_script_returns_zero_on_clean_root(self) -> None:
        """check_root_scripts returns 0 when no forbidden scripts exist."""
        spec = importlib.util.spec_from_file_location(
            "check_root_scripts",
            str(PROJECT_ROOT / "scripts" / "ci" / "check_root_scripts.py"),
        )
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        result = mod.check_root_scripts()
        assert result == 0

    def test_check_script_returns_one_on_violation(self) -> None:
        """check_root_scripts returns 1 when forbidden scripts are found."""
        spec = importlib.util.spec_from_file_location(
            "check_root_scripts",
            str(PROJECT_ROOT / "scripts" / "ci" / "check_root_scripts.py"),
        )
        assert spec is not None
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)

        # Mock PROJECT_ROOT.glob to return a fake forbidden file
        fake_path = type("FakePath", (), {"name": "run_hack.py"})()
        with patch.object(mod, "PROJECT_ROOT") as mock_root:
            mock_root.glob.return_value = [fake_path]
            result = mod.check_root_scripts()
            assert result == 1


class TestMigrationGuide:
    """Verify the migration guide exists and has required content."""

    def test_guide_exists(self) -> None:
        """scripts/MIGRATION_GUIDE.md must exist."""
        path = PROJECT_ROOT / "scripts" / "MIGRATION_GUIDE.md"
        assert path.exists()

    def test_guide_documents_old_scripts(self) -> None:
        """Migration guide must mention the old scripts."""
        content = (PROJECT_ROOT / "scripts" / "MIGRATION_GUIDE.md").read_text()
        assert "run_research.py" in content
        assert "run_market_pipeline.py" in content

    def test_guide_documents_api_equivalents(self) -> None:
        """Migration guide must document API alternatives."""
        content = (PROJECT_ROOT / "scripts" / "MIGRATION_GUIDE.md").read_text()
        assert "/api/v1/" in content

    def test_guide_documents_makefile_targets(self) -> None:
        """Migration guide must reference Makefile targets."""
        content = (PROJECT_ROOT / "scripts" / "MIGRATION_GUIDE.md").read_text()
        assert "make" in content.lower()
        assert "migrate" in content

    def test_guide_documents_cli(self) -> None:
        """Migration guide must mention the CLI."""
        content = (PROJECT_ROOT / "scripts" / "MIGRATION_GUIDE.md").read_text()
        assert "solstein_cli" in content or "CLI" in content
