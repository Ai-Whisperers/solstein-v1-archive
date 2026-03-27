"""Tests for STORY-128: Field Lineage CI Check.

Validates that:
- The CI check script correctly extracts model fields
- The CI check script correctly extracts documented fields
- Undocumented fields are detected and named specifically
- The --strict flag controls exit behavior
- All current domain model fields pass the check
"""

from pathlib import Path
from textwrap import dedent

import pytest

from scripts.ci.check_field_lineage import (
    extract_documented_fields,
    extract_model_fields,
    check_field_lineage,
    LINEAGE_DOC,
    MODELS_FILE,
)


class TestExtractModelFields:
    """Model field extraction from source code."""

    def test_extracts_company_fields(self) -> None:
        """Company model fields are extracted from models.py."""
        fields = extract_model_fields(MODELS_FILE)
        assert "Company" in fields
        # Spot-check well-known fields
        assert "name" in fields["Company"]
        assert "industry" in fields["Company"]
        assert "tenant_id" in fields["Company"]
        assert "ai_score" in fields["Company"]
        assert "ticker" in fields["Company"]

    def test_extracts_financial_metric_fields(self) -> None:
        """FinancialMetric model fields are extracted from models.py."""
        fields = extract_model_fields(MODELS_FILE)
        assert "FinancialMetric" in fields
        assert "revenue" in fields["FinancialMetric"]
        assert "profit_margin" in fields["FinancialMetric"]
        assert "employees" in fields["FinancialMetric"]
        assert "growth_rate" in fields["FinancialMetric"]

    def test_excludes_internal_fields(self) -> None:
        """Internal/infrastructure fields are excluded."""
        fields = extract_model_fields(MODELS_FILE)
        all_fields = fields["Company"] | fields["FinancialMetric"]
        assert "allow_empty_primary" not in all_fields
        assert "model_config" not in all_fields

    def test_does_not_include_other_models(self) -> None:
        """Only Company and FinancialMetric are extracted."""
        fields = extract_model_fields(MODELS_FILE)
        assert "MarketAnalysis" not in fields


class TestExtractDocumentedFields:
    """Documented field extraction from lineage markdown."""

    def test_extracts_simple_fields(self) -> None:
        """Simple backtick-quoted fields are extracted."""
        documented = extract_documented_fields(LINEAGE_DOC)
        assert "name" in documented
        assert "industry" in documented
        assert "ai_score" in documented

    def test_extracts_dotted_fields(self) -> None:
        """Dotted fields like financials.revenue are flattened."""
        documented = extract_documented_fields(LINEAGE_DOC)
        # financials.revenue should yield "revenue"
        assert "revenue" in documented
        assert "profit_margin" in documented

    def test_extracts_from_temp_file(self, tmp_path: Path) -> None:
        """Custom lineage file can be parsed."""
        lineage = tmp_path / "lineage.md"
        lineage.write_text(dedent("""\
            # Field Lineage
            | Field | Model |
            |-------|-------|
            | `alpha` | Company |
            | `parent.beta` | FinancialMetric |
        """))
        documented = extract_documented_fields(lineage)
        assert "alpha" in documented
        assert "beta" in documented


class TestCheckFieldLineage:
    """Integration tests for the full check."""

    def test_current_codebase_passes(self) -> None:
        """All current domain model fields are documented."""
        exit_code = check_field_lineage(strict=True)
        assert exit_code == 0, "Some domain model fields are undocumented in docs/field-lineage.md"

    def test_strict_mode_fails_on_undocumented(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Strict mode returns exit code 1 when fields are undocumented."""
        # Create a minimal models file with a field not in the lineage doc
        fake_models = tmp_path / "models.py"
        fake_models.write_text(dedent("""\
            from pydantic import BaseModel

            class FinancialMetric(BaseModel):
                revenue: float = 0.0

            class Company(BaseModel):
                name: str = ""
                secret_field: str = ""
        """))

        fake_lineage = tmp_path / "lineage.md"
        fake_lineage.write_text(dedent("""\
            # Lineage
            | Field | Model |
            |-------|-------|
            | `name` | Company |
            | `revenue` | FinancialMetric |
        """))

        import scripts.ci.check_field_lineage as module
        monkeypatch.setattr(module, "MODELS_FILE", fake_models)
        monkeypatch.setattr(module, "LINEAGE_DOC", fake_lineage)

        exit_code = check_field_lineage(strict=True)
        assert exit_code == 1

    def test_non_strict_mode_warns_only(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Non-strict mode returns 0 even with undocumented fields."""
        fake_models = tmp_path / "models.py"
        fake_models.write_text(dedent("""\
            from pydantic import BaseModel

            class FinancialMetric(BaseModel):
                revenue: float = 0.0

            class Company(BaseModel):
                name: str = ""
                mystery_field: int = 0
        """))

        fake_lineage = tmp_path / "lineage.md"
        fake_lineage.write_text(dedent("""\
            # Lineage
            | Field | Model |
            |-------|-------|
            | `name` | Company |
            | `revenue` | FinancialMetric |
        """))

        import scripts.ci.check_field_lineage as module
        monkeypatch.setattr(module, "MODELS_FILE", fake_models)
        monkeypatch.setattr(module, "LINEAGE_DOC", fake_lineage)

        exit_code = check_field_lineage(strict=False)
        assert exit_code == 0


class TestWarningOutput:
    """CI check names specific undocumented fields in output."""

    def test_warning_names_specific_field(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        """Warning output includes the specific undocumented field name."""
        fake_models = tmp_path / "models.py"
        fake_models.write_text(dedent("""\
            from pydantic import BaseModel

            class FinancialMetric(BaseModel):
                revenue: float = 0.0

            class Company(BaseModel):
                name: str = ""
                undocumented_xyz: str = ""
        """))

        fake_lineage = tmp_path / "lineage.md"
        fake_lineage.write_text(dedent("""\
            # Lineage
            | Field | Model |
            |-------|-------|
            | `name` | Company |
            | `revenue` | FinancialMetric |
        """))

        import scripts.ci.check_field_lineage as module
        monkeypatch.setattr(module, "MODELS_FILE", fake_models)
        monkeypatch.setattr(module, "LINEAGE_DOC", fake_lineage)

        check_field_lineage(strict=False)
        captured = capsys.readouterr()
        assert "undocumented_xyz" in captured.out
        assert "Company" in captured.out
