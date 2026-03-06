"""Tests for provenance module.

H1-H3: Tests for provenance tracking and validation.
"""

from datetime import datetime, timezone
from decimal import Decimal
from decimal import Decimal
from unittest.mock import Mock

import pytest

from solstein.data.provenance import (
    ConfidenceLevel,
    DataProvenance,
    FieldProvenance,
    ProvenanceError,
    ProvenanceValidator,
    ProvenanceViolation,
    SourceReliability,
    ValidationMode,
    validate_company_provenance,
)


class TestSourceReliability:
    """Tests for SourceReliability enum."""

    def test_reliability_values(self) -> None:
        assert SourceReliability.VERIFIED.value == 1.0
        assert SourceReliability.HIGH.value == 0.8
        assert SourceReliability.MEDIUM.value == 0.6
        assert SourceReliability.LOW.value == 0.4
        assert SourceReliability.UNVERIFIED.value == 0.2


class TestConfidenceLevel:
    """Tests for ConfidenceLevel enum."""

    def test_confidence_ranges(self) -> None:
        assert ConfidenceLevel.CERTAIN.min_score == 0.95
        assert ConfidenceLevel.HIGH.min_score == 0.80
        assert ConfidenceLevel.MEDIUM.min_score == 0.60
        assert ConfidenceLevel.LOW.min_score == 0.40
        assert ConfidenceLevel.UNCERTAIN.min_score == 0.0

    def test_from_score(self) -> None:
        assert ConfidenceLevel.from_score(0.97) == ConfidenceLevel.CERTAIN
        assert ConfidenceLevel.from_score(0.85) == ConfidenceLevel.HIGH
        assert ConfidenceLevel.from_score(0.70) == ConfidenceLevel.MEDIUM
        assert ConfidenceLevel.from_score(0.50) == ConfidenceLevel.LOW
        assert ConfidenceLevel.from_score(0.20) == ConfidenceLevel.UNCERTAIN


class TestFieldProvenance:
    """Tests for FieldProvenance dataclass."""

    def test_default_values(self) -> None:
        fp = FieldProvenance()
        assert fp.source is None
        assert fp.timestamp is None
        assert fp.confidence == 1.0
        assert fp.reliability == SourceReliability.VERIFIED

    def test_to_dict(self) -> None:
        fp = FieldProvenance(
            source="sec_edgar",
            timestamp=datetime(2024, 1, 1),
            confidence=0.95,
            reliability=SourceReliability.HIGH,
        )
        result = fp.to_dict()

        assert result["source"] == "sec_edgar"
        assert result["confidence"] == 0.95
        assert result["reliability"] == "high"


class TestDataProvenance:
    """Tests for DataProvenance dataclass."""

    def test_empty_provenance(self) -> None:
        dp = DataProvenance()
        assert dp.fields == {}
        assert dp.overall_confidence == 1.0

    def test_get_field_provenance(self) -> None:
        dp = DataProvenance()
        dp.fields["revenue"] = FieldProvenance(source="sec_edgar")

        result = dp.get_field_provenance("revenue")
        assert result.source == "sec_edgar"

    def test_get_field_provenance_missing(self) -> None:
        dp = DataProvenance()
        result = dp.get_field_provenance("missing")

        assert result.source is None
        assert result.confidence == 0.0

    def test_has_field(self) -> None:
        dp = DataProvenance()
        dp.fields["revenue"] = FieldProvenance()

        assert dp.has_field("revenue") is True
        assert dp.has_field("missing") is False

    def test_add_field(self) -> None:
        dp = DataProvenance()
        dp.add_field("revenue", source="sec_edgar", confidence=0.95)

        assert dp.fields["revenue"].source == "sec_edgar"
        assert dp.fields["revenue"].confidence == 0.95

    def test_calculate_overall_confidence(self) -> None:
        dp = DataProvenance()
        dp.fields["revenue"] = FieldProvenance(confidence=0.9)
        dp.fields["growth"] = FieldProvenance(confidence=0.8)

        result = dp.calculate_overall_confidence()
        assert result == pytest.approx(0.85, 0.01)  # Average


class TestProvenanceViolation:
    """Tests for ProvenanceViolation dataclass."""

    def test_creation(self) -> None:
        pv = ProvenanceViolation(
            field="revenue",
            violation_type="missing_provenance",
            message="No provenance for revenue",
        )

        assert pv.field == "revenue"
        assert pv.violation_type == "missing_provenance"
        assert pv.severity == "error"


class TestProvenanceValidator:
    """Tests for ProvenanceValidator class."""

    def test_validate_field_with_provenance(self) -> None:
        validator = ProvenanceValidator()
        provenance = DataProvenance()
        provenance.fields["revenue"] = FieldProvenance(source="sec_edgar")

        violations = validator.validate_field("revenue", 1000000, Decimal("1000000"), provenance)

        assert len(violations) == 0

    def test_validate_field_missing_provenance(self) -> None:
        validator = ProvenanceValidator()
        provenance = DataProvenance()

        violations = validator.validate_field("revenue", 1000000, Decimal("1000000"), provenance)

        assert len(violations) == 1
        assert violations[0].violation_type == "missing_provenance"

    def test_validate_field_low_confidence(self) -> None:
        validator = ProvenanceValidator()
        provenance = DataProvenance()
        provenance.fields["revenue"] = FieldProvenance(source="web_scrape", confidence=0.3)

        violations = validator.validate_field("revenue", 1000000, Decimal("1000000"), provenance)

        assert len(violations) == 1
        assert violations[0].violation_type == "low_confidence"

    def test_validate_field_unverified_source(self) -> None:
        validator = ProvenanceValidator()
        provenance = DataProvenance()
        provenance.fields["revenue"] = FieldProvenance(source="unknown", reliability=SourceReliability.UNVERIFIED)

        violations = validator.validate_field("revenue", 1000000, Decimal("1000000"), provenance)

        assert len(violations) == 1
        assert violations[0].violation_type == "unverified_source"

    def test_validate_field_stale_data(self) -> None:
        validator = ProvenanceValidator()
        provenance = DataProvenance()
        provenance.fields["revenue"] = FieldProvenance(
            source="sec_edgar",
            timestamp=datetime(2020, 1, 1, tzinfo=timezone.utc),  # Very old
        )

        violations = validator.validate_field("revenue", 1000000, Decimal("1000000"), provenance)

        assert len(violations) == 1
        assert violations[0].violation_type == "stale_data"

    def test_strict_mode_requires_provenance(self) -> None:
        validator = ProvenanceValidator(mode=ValidationMode.STRICT)
        provenance = DataProvenance()  # Empty

        violations = validator.validate_field("revenue", 1000000, Decimal("1000000"), provenance)

        assert len(violations) == 1
        assert violations[0].severity == "error"

    def test_lenient_mode_allows_missing(self) -> None:
        validator = ProvenanceValidator(mode=ValidationMode.LENIENT)
        provenance = DataProvenance()  # Empty

        violations = validator.validate_field("revenue", 1000000, Decimal("1000000"), provenance)

        assert len(violations) == 1
        assert violations[0].severity == "warning"

    def test_validate_company(self) -> None:
        validator = ProvenanceValidator(required_fields={"revenue", "growth"})

        company = Mock()
        company.revenue = 1000000
        company.growth_rate = 0.5
        company.provenance = DataProvenance()
        company.provenance.fields["revenue"] = FieldProvenance(source="sec_edgar")
        # growth has no provenance

        violations = validator.validate_company(company)

        assert len(violations) == 1
        assert violations[0].field == "growth"

    def test_is_field_complete(self) -> None:
        validator = ProvenanceValidator()
        provenance = DataProvenance()
        provenance.fields["revenue"] = FieldProvenance(
            source="sec_edgar",
            confidence=0.95,
            reliability=SourceReliability.VERIFIED,
        )

        is_complete = validator.is_field_complete("revenue", provenance)

        assert is_complete is True


class TestValidateCompanyProvenance:
    """Tests for validate_company_provenance function."""

    def test_valid_company(self) -> None:
        company = Mock()
        company.revenue = 1000000
        company.growth_rate = 0.5
        company.profit_margin = 0.1
        company.funding_total = 5000000
        company.valuation = 10000000
        company.employee_count = 100
        company.ebitda = 200000
        company.provenance = DataProvenance()
        company.provenance.fields["revenue"] = FieldProvenance(source="sec_edgar")
        company.provenance.fields["growth_rate"] = FieldProvenance(source="crunchbase")
        company.provenance.fields["profit_margin"] = FieldProvenance(source="sec_edgar")
        company.provenance.fields["funding_total"] = FieldProvenance(source="crunchbase")
        company.provenance.fields["valuation"] = FieldProvenance(source="pitchbook")
        company.provenance.fields["employee_count"] = FieldProvenance(source="linkedin")
        company.provenance.fields["ebitda"] = FieldProvenance(source="sec_edgar")

        violations = validate_company_provenance(company)

        assert len(violations) == 0

    def test_missing_provenance(self) -> None:
        company = Mock()
        company.revenue = 1000000
        company.growth_rate = 0.5
        company.provenance = DataProvenance()
        company.provenance.fields["revenue"] = FieldProvenance(source="sec_edgar")
        company.provenance.fields["growth_rate"] = FieldProvenance(source="crunchbase")

        violations = validate_company_provenance(company)

        assert len(violations) == 0

    def test_missing_provenance(self) -> None:
        company = Mock()
        company.revenue = 1000000
        company.growth_rate = 0.5
        company.provenance = DataProvenance()
        # No provenance for any fields

        violations = validate_company_provenance(company)

        assert len(violations) > 0


class TestProvenanceError:
    """Tests for ProvenanceError exception."""

    def test_creation(self) -> None:
        error = ProvenanceError("Test error", code="TEST_ERROR")

        assert str(error) == "Test error"
        assert error.code == "TEST_ERROR"

    def test_with_violations(self) -> None:
        violations = [
            ProvenanceViolation("revenue", "missing_provenance", "No source"),
        ]
        error = ProvenanceError(
            "Validation failed",
            code="PROVENANCE_INVALID",
            violations=violations,
        )

        assert len(error.violations) == 1
        assert error.violations[0].field == "revenue"
