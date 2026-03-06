"""Comprehensive unit tests for scoring module - EPIC-012"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from solstein.analytics.scoring import calculate_composite_score, classify_company
from solstein.domain.models import CompanyClassification


class TestCompositeScoreCalculation:
    """Test composite score calculation."""

    def test_high_scoring_company(self):
        """High scoring inputs should produce high composite score."""
        result = calculate_composite_score(
            growth_score=9.0,
            financial_health_score=8.5,
            competitive_position_score=9.5
        )
        assert result.composite_score > 8.0
        assert result.classification == CompanyClassification.PHOENIX

    def test_medium_scoring_company(self):
        """Medium scoring inputs should produce medium composite score."""
        result = calculate_composite_score(
            growth_score=5.0,
            financial_health_score=6.0,
            competitive_position_score=5.5
        )
        assert 4.0 <= result.composite_score < 7.0
        assert result.classification == CompanyClassification.SALT

    def test_low_scoring_company(self):
        """Low scoring inputs should produce low composite score."""
        result = calculate_composite_score(
            growth_score=2.0,
            financial_health_score=3.0,
            competitive_position_score=2.5
        )
        assert result.composite_score < 4.0
        assert result.classification == CompanyClassification.LEAD

    def test_classification_thresholds(self):
        """Test classification boundary conditions."""
        # Phoenix threshold (≥7.0)
        assert classify_company(7.0) == CompanyClassification.PHOENIX
        assert classify_company(6.99) == CompanyClassification.SALT

        # Salt threshold (4.5-6.99)
        assert classify_company(4.5) == CompanyClassification.SALT
        assert classify_company(4.49) == CompanyClassification.LEAD

        # Lead threshold (<4.5)
        assert classify_company(0.0) == CompanyClassification.LEAD
        assert classify_company(4.0) == CompanyClassification.LEAD


class TestScoringBreakdown:
    """Test scoring breakdown and component tracking."""

    def test_breakdown_contains_all_scores(self):
        """Scoring breakdown should include all component scores."""
        result = calculate_composite_score(8.0, 7.5, 8.5)

        assert "growth_score" in result.breakdown
        assert "financial_health_score" in result.breakdown
        assert "competitive_position_score" in result.breakdown
        assert result.breakdown["growth_score"] == 8.0

    def test_classification_in_breakdown(self):
        """Classification should be included in breakdown."""
        result = calculate_composite_score(9.0, 9.0, 9.0)
        assert "classification" in result.breakdown
        assert result.breakdown["classification"] == "Phoenix"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
