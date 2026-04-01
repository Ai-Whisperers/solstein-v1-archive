"""Tests for STORY-119: Split unified_loader.py into Separate Modules.

Verifies that:
- unified_loader.py is a thin orchestration layer (<=100 lines)
- No hardcoded dates or market names exist
- All split modules are independently importable
- Each module has clear single responsibility
- Backward compatibility maintained via unified_loader re-exports
"""

from pathlib import Path

from solstein.data.unified import (
    BatchEnrichmentOutcome,
    UnifiedCompany,
    UnifiedCompanyLoader,
    enrich_from_connectors,
    format_enrichment_error,
    merge_companies,
)
from solstein.data.unified.batch_outcomes import (
    BatchEnrichmentOutcome as BEO_Direct,
)
from solstein.data.unified.company import UnifiedCompany as UC_Direct
from solstein.data.unified.enrichment import (
    enrich_from_connectors as efc_direct,
)
from solstein.data.unified.error_tracking import (
    format_enrichment_error as fee_direct,
)
from solstein.data.unified.merger import merge_companies as mc_direct
from solstein.data.unified_loader import (
    UnifiedCompany as UC_Compat,
)
from solstein.data.unified_loader import (
    UnifiedCompanyLoader as UCL_Compat,
)
from solstein.data.unified_loader import (
    categorize_error as ce_compat,
)
from solstein.data.unified_loader import (
    convert_to_unified as ctu_compat,
)
from solstein.data.unified_loader import (
    format_enrichment_error as fee_compat,
)
from solstein.data.unified_loader import (
    merge_companies as mc_compat,
)
from solstein.data.unified_loader import (
    unified_loader,
)

SRC = Path("src/solstein")
UNIFIED_DIR = SRC / "data" / "unified"


class TestUnifiedLoaderOrchestration:
    """Verify unified_loader.py is a thin orchestration layer."""

    def test_unified_loader_under_100_lines(self) -> None:
        loader_file = SRC / "data" / "unified_loader.py"
        line_count = len(loader_file.read_text().splitlines())
        assert line_count <= 100, (
            f"unified_loader.py is {line_count} lines (limit: 100)"
        )

    def test_unified_loader_is_reexport_only(self) -> None:
        """Verify it only re-exports, no business logic."""
        content = (SRC / "data" / "unified_loader.py").read_text()
        assert "def " not in content or content.count("def ") == 0, (
            "unified_loader.py should contain no function definitions"
        )
        assert "class " not in content or content.count("class ") == 0, (
            "unified_loader.py should contain no class definitions"
        )


class TestNoHardcodedValues:
    """Verify no hardcoded dates or market names."""

    def test_no_hardcoded_date(self) -> None:
        for py_file in UNIFIED_DIR.rglob("*.py"):
            content = py_file.read_text()
            assert "2026-02-23" not in content, (
                f"{py_file.name} contains hardcoded date '2026-02-23'"
            )

    def test_no_hardcoded_dutch_market(self) -> None:
        for py_file in UNIFIED_DIR.rglob("*.py"):
            content = py_file.read_text()
            assert "dutch_market" not in content, (
                f"{py_file.name} contains hardcoded 'dutch_market'"
            )

    def test_no_hardcoded_date_in_loader(self) -> None:
        content = (SRC / "data" / "unified_loader.py").read_text()
        assert "2026-02-23" not in content


class TestModuleStructure:
    """Verify the split module structure exists."""

    def test_unified_package_exists(self) -> None:
        assert (UNIFIED_DIR / "__init__.py").exists()

    def test_company_module_exists(self) -> None:
        assert (UNIFIED_DIR / "company.py").exists()

    def test_enrichment_module_exists(self) -> None:
        assert (UNIFIED_DIR / "enrichment.py").exists()

    def test_error_tracking_module_exists(self) -> None:
        assert (UNIFIED_DIR / "error_tracking.py").exists()

    def test_merger_module_exists(self) -> None:
        assert (UNIFIED_DIR / "merger.py").exists()

    def test_batch_outcomes_module_exists(self) -> None:
        assert (UNIFIED_DIR / "batch_outcomes.py").exists()

    def test_each_module_under_500_lines(self) -> None:
        for py_file in sorted(UNIFIED_DIR.glob("*.py")):
            if py_file.name == "__pycache__":
                continue
            line_count = len(py_file.read_text().splitlines())
            assert line_count <= 500, (
                f"{py_file.name} is {line_count} lines (limit: 500)"
            )


class TestModuleImportability:
    """Verify each split module can be imported."""

    def test_import_company(self) -> None:
        assert UC_Direct is UnifiedCompany

    def test_import_enrichment(self) -> None:
        assert efc_direct is enrich_from_connectors

    def test_import_error_tracking(self) -> None:
        assert fee_direct is format_enrichment_error

    def test_import_merger(self) -> None:
        assert mc_direct is merge_companies

    def test_import_batch_outcomes(self) -> None:
        assert BEO_Direct is BatchEnrichmentOutcome


class TestBackwardCompatibility:
    """Verify callers of unified_loader still work."""

    def test_global_instance_available(self) -> None:
        assert unified_loader is not None
        assert isinstance(unified_loader, UnifiedCompanyLoader)

    def test_reexports_classes(self) -> None:
        assert UC_Compat is UnifiedCompany
        assert UCL_Compat is UnifiedCompanyLoader

    def test_reexports_functions(self) -> None:
        assert callable(ce_compat)
        assert callable(ctu_compat)
        assert callable(fee_compat)
        assert callable(mc_compat)
