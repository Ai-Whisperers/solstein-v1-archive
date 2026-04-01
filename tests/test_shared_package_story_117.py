"""Tests for STORY-117: Fix Circular Import Risk -- Introduce shared/ Package.

Verifies that:
- shared/ package exists with zero application-layer imports
- shared/ modules are importable
- Import purity check script works
- python -c "import solstein" completes without errors
"""

import subprocess
import sys
from pathlib import Path

import solstein.shared  # noqa: F401
from solstein.shared.constants import (
    CONFIDENCE_HIGH,
    DEFAULT_HTTP_TIMEOUT_S,
    DEFAULT_MAX_RETRIES,
    SCORE_MAX,
    SCORE_MIN,
)
from solstein.shared.exceptions import (
    ConfigurationError,
    DataIntegrityError,
    ExternalServiceError,
    NotFoundError,
    SolsteinError,
    ValidationError,
)
from solstein.shared.logging_config import get_logger

SRC = Path("src/solstein")


class TestSharedPackageExists:
    """Verify shared/ package structure."""

    def test_shared_init_exists(self) -> None:
        assert (SRC / "shared" / "__init__.py").exists()

    def test_shared_exceptions_exists(self) -> None:
        assert (SRC / "shared" / "exceptions.py").exists()

    def test_shared_constants_exists(self) -> None:
        assert (SRC / "shared" / "constants.py").exists()

    def test_shared_logging_config_exists(self) -> None:
        assert (SRC / "shared" / "logging_config.py").exists()


class TestSharedImportability:
    """Verify shared/ modules can be imported."""

    def test_import_shared(self) -> None:
        assert solstein.shared is not None

    def test_import_exceptions(self) -> None:
        assert issubclass(ConfigurationError, SolsteinError)
        assert issubclass(ValidationError, SolsteinError)
        assert issubclass(ExternalServiceError, SolsteinError)
        assert issubclass(DataIntegrityError, SolsteinError)
        assert issubclass(NotFoundError, SolsteinError)

    def test_import_constants(self) -> None:
        assert DEFAULT_HTTP_TIMEOUT_S == 30
        assert DEFAULT_MAX_RETRIES == 3
        assert SCORE_MIN < SCORE_MAX
        assert CONFIDENCE_HIGH > 0.0

    def test_import_logging_config(self) -> None:
        logger = get_logger("test")
        assert logger is not None


class TestSharedPurity:
    """Verify shared/ has zero application-layer imports."""

    def test_purity_check_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/ci/check_shared_purity.py"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"shared/ purity check failed:\n{result.stdout}\n{result.stderr}"
        )


class TestExceptionHierarchy:
    """Verify exception classes work correctly."""

    def test_solstein_error_with_code(self) -> None:
        err = SolsteinError("test", error_code="TEST_001")
        assert str(err) == "test"
        assert err.error_code == "TEST_001"

    def test_external_service_error(self) -> None:
        err = ExternalServiceError(
            "API down",
            service="yahoo_finance",
            retryable=True,
        )
        assert err.service == "yahoo_finance"
        assert err.retryable is True
        assert err.error_code == "EXTERNAL_SERVICE_ERROR"

    def test_not_found_error(self) -> None:
        err = NotFoundError("Company X not found", resource_type="company")
        assert err.resource_type == "company"


class TestArchitectureDocumentation:
    """Verify import graph documentation exists."""

    def test_import_graph_doc_exists(self) -> None:
        assert Path("docs/architecture/import-graph.md").exists()

    def test_import_graph_mentions_shared(self) -> None:
        content = Path("docs/architecture/import-graph.md").read_text()
        assert "shared/" in content
        assert "zero" in content.lower() or "nothing" in content.lower()
