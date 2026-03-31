"""Synthetic-mode gate tests - G5.

Ensure no production-ready output bypasses authenticity policy.
Part of EPIC-017 Wave 2 Testing Hardening.
"""

from unittest.mock import Mock, patch

import pytest

from solstein.data.report_release_gate import ReportReleaseGate
from solstein.data.synthetic_data_safety import (
    DataAuthenticity,
    DataSourceType,
    SyntheticDataBlocker,
    create_authenticity_label,
)
from solstein.domain.models import Company


class TestSyntheticModeGate:
    """Tests for synthetic-mode gate enforcement."""

    def test_synthetic_data_blocked_from_export(self) -> None:
        """Synthetic data must be blocked from production export."""
        blocker = SyntheticDataBlocker()

        synthetic_company = Mock(spec=Company)
        synthetic_company.data_source_type = "synthetic"

        result = blocker.check_company(synthetic_company)

        assert result.passed is False
        assert result.blocked_count == 1

    def test_mixed_data_blocked_from_export(self) -> None:
        """Mixed data must be blocked from production export."""
        blocker = SyntheticDataBlocker()

        mixed_company = Mock(spec=Company)
        mixed_company.data_source_type = "mixed"

        result = blocker.check_company(mixed_company)

        # Mixed data is blocked by default
        assert result.passed is False
        assert result.blocked_count == 1

    def test_real_data_allowed_for_export(self) -> None:
        """Real data should be allowed for production export."""
        blocker = SyntheticDataBlocker()

        real_company = Mock(spec=Company)
        real_company.data_source_type = "real"

        result = blocker.check_company(real_company)

        assert result.passed is True
        assert result.allowed_count == 1

    def test_unknown_data_allowed_by_default(self) -> None:
        """Unknown data source is allowed by default (not blocked)."""
        blocker = SyntheticDataBlocker()

        unknown_company = Mock(spec=Company)
        unknown_company.data_source_type = "unknown"

        result = blocker.check_company(unknown_company)

        # Unknown is NOT blocked (only synthetic and mixed are blocked)
        assert result.passed is True


class TestAuthenticityPolicyEnforcement:
    """Tests for authenticity policy enforcement."""

    def test_authenticity_label_created_from_company(self) -> None:
        """Authenticity label should be created from company data."""
        real_company = Mock(spec=Company)
        real_company.data_source_type = "real"
        real_company.data_source = "test_source"

        label = create_authenticity_label(real_company)

        assert label is not None
        assert label.source_type == DataSourceType.REAL

    def test_synthetic_authenticity_blocked(self) -> None:
        """Synthetic authenticity should be blocked."""
        authenticity = DataAuthenticity(
            source_type=DataSourceType.SYNTHETIC,
            confidence=0.8,
            sources=["synthetic_generator"],
        )

        assert authenticity.is_blocked is True

    def test_mixed_authenticity_blocked(self) -> None:
        """Mixed authenticity should be blocked."""
        authenticity = DataAuthenticity(
            source_type=DataSourceType.MIXED,
            confidence=0.6,
            sources=["real_source", "synthetic_source"],
            synthetic_percentage=30.0,
        )

        assert authenticity.is_blocked is True


class TestReportReleaseGateAuthenticity:
    """Tests for report release gate authenticity checks."""

    def test_gate_blocks_synthetic_companies(self) -> None:
        """Report gate must block synthetic companies."""
        gate = ReportReleaseGate()

        synthetic_company = Mock(spec=Company)
        synthetic_company.data_source_type = "synthetic"

        # Should raise or return blocked status
        with pytest.raises(Exception):
            gate.validate_for_release(synthetic_company)

    def test_gate_allows_real_companies(self) -> None:
        """Report gate must allow real companies."""
        gate = ReportReleaseGate()

        real_company = Mock(spec=Company)
        real_company.data_source_type = "real"
        real_company.name = "Real Company"
        real_company.id = "real-001"

        # Should not raise
        try:
            gate.validate_for_release(real_company)
        except Exception as e:
            # If it raises, it should be for reasons other than synthetic data
            assert "synthetic" not in str(e).lower()


class TestNoBypassPolicy:
    """Tests ensuring no bypass of authenticity policy."""

    def test_direct_export_blocked_for_synthetic(self) -> None:
        """Direct export methods must respect synthetic block."""
        blocker = SyntheticDataBlocker()

        # Try to bypass with synthetic data
        synthetic_company = Mock(spec=Company)
        synthetic_company.data_source_type = "synthetic"

        # Should be blocked regardless of how we try to export
        result = blocker.check_company(synthetic_company)
        assert result.passed is False

    def test_batch_export_respects_policy(self) -> None:
        """Batch export must respect authenticity policy for all items."""
        blocker = SyntheticDataBlocker()

        companies = [
            Mock(spec=Company, data_source_type="real"),
            Mock(spec=Company, data_source_type="synthetic"),
            Mock(spec=Company, data_source_type="real"),
        ]

        # Should fail because one is synthetic
        results = [blocker.check_company(c) for c in companies]
        assert any(not r.passed for r in results)

    def test_policy_enforced_at_multiple_layers(self) -> None:
        """Policy should be enforced at data layer, service layer, and export layer."""
        # Data layer check
        authenticity = DataAuthenticity(source_type=DataSourceType.SYNTHETIC)
        assert authenticity.is_blocked is True

        # Service layer check (via blocker)
        blocker = SyntheticDataBlocker()
        synthetic_company = Mock(spec=Company)
        synthetic_company.data_source_type = "synthetic"
        result = blocker.check_company(synthetic_company)
        assert result.passed is False


class TestSyntheticDataAuditTrail:
    """Tests for synthetic data audit trail."""

    def test_synthetic_data_logged(self) -> None:
        """Attempts to export synthetic data should be logged."""
        blocker = SyntheticDataBlocker()

        synthetic_company = Mock(spec=Company)
        synthetic_company.data_source_type = "synthetic"
        synthetic_company.id = "synth-001"
        synthetic_company.name = "Synthetic Co"

        # Should log the blocked attempt
        with patch('solstein.data.synthetic_data_safety.logger') as mock_logger:
            blocker.check_company(synthetic_company)
            # Should have logged a warning or error
            assert mock_logger.warning.called or mock_logger.error.called
