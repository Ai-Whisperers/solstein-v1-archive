"""Tests for synthetic data safety module.

L1: Tests for synthetic-only interim safety controls.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from solstein.data.synthetic_data_safety import (
    AuthenticityLabel,
    DataAuthenticity,
    DataSourceType,
    SyntheticDataBlocker,
    SyntheticDataError,
    create_authenticity_label,
)


class TestDataSourceType:
    """Tests for DataSourceType enum."""

    def test_all_types_exist(self) -> None:
        assert DataSourceType.REAL.value == "real"
        assert DataSourceType.SYNTHETIC.value == "synthetic"
        assert DataSourceType.MIXED.value == "mixed"
        assert DataSourceType.UNKNOWN.value == "unknown"

    def test_is_blocked(self) -> None:
        assert DataSourceType.SYNTHETIC.is_blocked is True
        assert DataSourceType.MIXED.is_blocked is True
        assert DataSourceType.REAL.is_blocked is False
        assert DataSourceType.UNKNOWN.is_blocked is False


class TestDataAuthenticity:
    """Tests for DataAuthenticity dataclass."""

    def test_default_values(self) -> None:
        auth = DataAuthenticity()
        assert auth.source_type == DataSourceType.UNKNOWN
        assert auth.synthetic_percentage == 0.0
        assert auth.is_blocked is False

    def test_is_blocked_with_synthetic(self) -> None:
        auth = DataAuthenticity(source_type=DataSourceType.SYNTHETIC)
        assert auth.is_blocked is True

    def test_is_blocked_with_mixed(self) -> None:
        auth = DataAuthenticity(source_type=DataSourceType.MIXED, synthetic_percentage=30.0)
        assert auth.is_blocked is True

    def test_to_dict(self) -> None:
        auth = DataAuthenticity(
            source_type=DataSourceType.REAL,
            confidence=0.95,
            sources=["sec_edgar", "crunchbase"],
        )
        result = auth.to_dict()

        assert result["source_type"] == "real"
        assert result["confidence"] == 0.95
        assert result["sources"] == ["sec_edgar", "crunchbase"]
        assert result["is_blocked"] is False

    def test_from_company_with_synthetic_flag(self) -> None:
        company = Mock()
        company.data_source_type = "synthetic"

        auth = DataAuthenticity.from_company(company)
        assert auth.source_type == DataSourceType.SYNTHETIC
        assert auth.is_blocked is True

    def test_from_company_with_mixed_flag(self) -> None:
        company = Mock()
        company.data_source_type = "mixed"
        company.synthetic_percentage = 25.0

        auth = DataAuthenticity.from_company(company)
        assert auth.source_type == DataSourceType.MIXED
        assert auth.synthetic_percentage == 25.0

    def test_from_company_with_real_flag(self) -> None:
        company = Mock()
        company.data_source_type = "real"

        auth = DataAuthenticity.from_company(company)
        assert auth.source_type == DataSourceType.REAL
        assert auth.is_blocked is False

    def test_from_company_default_unknown(self) -> None:
        company = Mock()
        company.data_source_type = None

        auth = DataAuthenticity.from_company(company)
        assert auth.source_type == DataSourceType.UNKNOWN


class TestAuthenticityLabel:
    """Tests for AuthenticityLabel dataclass."""

    def test_creation(self) -> None:
        label = AuthenticityLabel(
            source_type=DataSourceType.REAL,
            confidence=0.9,
        )
        assert label.source_type == DataSourceType.REAL
        assert label.confidence == 0.9
        assert label.verified_at is not None

    def test_to_dict(self) -> None:
        label = AuthenticityLabel(
            source_type=DataSourceType.SYNTHETIC,
            confidence=0.8,
            verification_method="manual_review",
        )
        result = label.to_dict()

        assert result["source_type"] == "synthetic"
        assert result["confidence"] == 0.8
        assert result["verification_method"] == "manual_review"
        assert "verified_at" in result
        assert "is_blocked" in result


class TestCreateAuthenticityLabel:
    """Tests for create_authenticity_label helper."""

    def test_real_data(self) -> None:
        company = Mock()
        company.data_source_type = "real"
        company.data_sources = ["sec_edgar", "crunchbase"]

        label = create_authenticity_label(company)

        assert label.source_type == DataSourceType.REAL
        assert "sec_edgar" in label.sources
        assert label.blocked_for_export is False

    def test_synthetic_data_blocked(self) -> None:
        company = Mock()
        company.data_source_type = "synthetic"

        label = create_authenticity_label(company)

        assert label.source_type == DataSourceType.SYNTHETIC
        assert label.blocked_for_export is True

    def test_mixed_data_blocked(self) -> None:
        company = Mock()
        company.data_source_type = "mixed"
        company.synthetic_percentage = 50.0

        label = create_authenticity_label(company)

        assert label.source_type == DataSourceType.MIXED
        assert label.synthetic_percentage == 50.0
        assert label.blocked_for_export is True


class TestSyntheticDataError:
    """Tests for SyntheticDataError exception."""

    def test_basic_error(self) -> None:
        error = SyntheticDataError("Synthetic data detected")

        assert str(error) == "Synthetic data detected"
        assert error.code == "SYNTHETIC_DATA_BLOCKED"
        assert error.details == {}

    def test_error_with_details(self) -> None:
        error = SyntheticDataError(
            "Cannot export synthetic data",
            details={"company": "TestCo", "source_type": "synthetic"},
        )

        assert error.details["company"] == "TestCo"


class TestSyntheticDataBlocker:
    """Tests for SyntheticDataBlocker class."""

    def test_default_settings(self) -> None:
        blocker = SyntheticDataBlocker()
        assert blocker.block_synthetic is True
        assert blocker.block_mixed is True
        assert blocker.synthetic_threshold_percentage == 0.0

    def test_custom_settings(self) -> None:
        blocker = SyntheticDataBlocker(
            block_synthetic=True,
            block_mixed=False,
            synthetic_threshold_percentage=50.0,
        )
        assert blocker.block_mixed is False
        assert blocker.synthetic_threshold_percentage == 50.0

    def test_check_company_real_passes(self) -> None:
        blocker = SyntheticDataBlocker()
        company = Mock()
        company.data_source_type = "real"

        result = blocker.check_company(company)

        assert result.passed is True
        assert len(result.violations) == 0

    def test_check_company_synthetic_blocked(self) -> None:
        blocker = SyntheticDataBlocker()
        company = Mock()
        company.name = "TestCo"
        company.data_source_type = "synthetic"

        result = blocker.check_company(company)

        assert result.passed is False
        assert len(result.violations) == 1
        assert result.violations[0].source_type == DataSourceType.SYNTHETIC

    def test_check_company_mixed_blocked(self) -> None:
        blocker = SyntheticDataBlocker()
        company = Mock()
        company.name = "TestCo"
        company.data_source_type = "mixed"
        company.synthetic_percentage = 30.0

        result = blocker.check_company(company)

        assert result.passed is False
        assert result.violations[0].source_type == DataSourceType.MIXED

    def test_check_company_mixed_below_threshold_passes(self) -> None:
        blocker = SyntheticDataBlocker(synthetic_threshold_percentage=50.0)
        company = Mock()
        company.name = "TestCo"
        company.data_source_type = "mixed"
        company.synthetic_percentage = 30.0  # Below 50% threshold

        result = blocker.check_company(company)

        assert result.passed is True
        assert len(result.violations) == 0

    def test_check_companies_all_real(self) -> None:
        blocker = SyntheticDataBlocker()

        company1 = Mock()
        company1.data_source_type = "real"
        company2 = Mock()
        company2.data_source_type = "real"

        result = blocker.check_companies([company1, company2])

        assert result.passed is True
        assert result.blocked_count == 0
        assert result.allowed_count == 2

    def test_check_companies_some_synthetic(self) -> None:
        blocker = SyntheticDataBlocker()

        real_company = Mock()
        real_company.name = "RealCo"
        real_company.data_source_type = "real"

        synthetic_company = Mock()
        synthetic_company.name = "SyntheticCo"
        synthetic_company.data_source_type = "synthetic"

        result = blocker.check_companies([real_company, synthetic_company])

        assert result.passed is False
        assert result.blocked_count == 1
        assert result.allowed_count == 1

    def test_ensure_safe_all_real(self) -> None:
        blocker = SyntheticDataBlocker()

        company = Mock()
        company.data_source_type = "real"

        # Should not raise
        blocker.ensure_safe([company])

    def test_ensure_safe_with_synthetic_raises(self) -> None:
        blocker = SyntheticDataBlocker()

        company = Mock()
        company.name = "TestCo"
        company.data_source_type = "synthetic"

        with pytest.raises(SyntheticDataError) as exc_info:
            blocker.ensure_safe([company])

        # Error message should indicate synthetic data was blocked
        assert "synthetic" in str(exc_info.value).lower()
        assert exc_info.value.code == "SYNTHETIC_DATA_BLOCKED"

    def test_get_authenticity_summary(self) -> None:

        blocker = SyntheticDataBlocker()

        company = Mock()
        company.name = "TestCo"
        company.data_source_type = "synthetic"

        with pytest.raises(SyntheticDataError) as exc_info:
            blocker.ensure_safe([company])

        # Error message should indicate synthetic data was blocked
        assert "synthetic" in str(exc_info.value).lower()
        assert exc_info.value.code == "SYNTHETIC_DATA_BLOCKED"
        blocker = SyntheticDataBlocker()

        company = Mock()
        company.name = "TestCo"
        company.data_source_type = "synthetic"

        with pytest.raises(SyntheticDataError) as exc_info:
            blocker.ensure_safe([company])

        assert "TestCo" in str(exc_info.value)
        assert exc_info.value.code == "SYNTHETIC_DATA_BLOCKED"

    def test_get_authenticity_summary(self) -> None:
        blocker = SyntheticDataBlocker()

        real_company = Mock()
        real_company.data_source_type = "real"

        synthetic_company = Mock()
        synthetic_company.data_source_type = "synthetic"

        summary = blocker.get_authenticity_summary([real_company, synthetic_company])

        assert summary["total"] == 2
        assert summary["real"] == 1
        assert summary["synthetic"] == 1
        assert summary["blocked"] == 1
        assert summary["allowed"] == 1
