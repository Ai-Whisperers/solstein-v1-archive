"""Unit tests for GrowthMomentumScorer with facts integration.

Tests cover:
- Growth scoring with financial facts from repository
- Fact merging into financial metrics
- Confidence level conversion
- Backward compatibility with existing scoring
"""

import uuid
from unittest.mock import MagicMock

import pytest

from solstein.analytics.scorers._shared import confidence_to_level
from solstein.analytics.scorers.growth_momentum import GrowthMomentumScorer
from solstein.domain.facts import Fact
from solstein.domain.models import ConfidenceLevel, FinancialMetric


class TestGrowthScorerWithFacts:
    """Tests for growth scorer with facts integration."""

    @pytest.fixture
    def scorer(self):
        """Create a GrowthMomentumScorer instance."""
        return GrowthMomentumScorer()

    @pytest.fixture
    def mock_fact_repo(self):
        """Create a mock FactRepository."""
        return MagicMock()

    def test_score_without_facts(self, scorer):
        """Test scoring works without facts (backward compatibility)."""
        financials = FinancialMetric(
            revenue=1000000,
            growth_rate=20,
            employees=50,
            profit_margin=15,
        )

        score, explanation = scorer.score(financials)

        assert 0 <= score <= 10
        assert explanation.final_score == score
        assert len(explanation.components) > 0

    def test_score_with_facts_no_repo(self, scorer):
        """Test scoring with facts parameter but no repo provided."""
        financials = FinancialMetric(revenue=1000000)

        score, explanation = scorer.score(financials, fact_repo=None, company_id="test-company")

        assert 0 <= score <= 10

    def test_score_with_facts_no_company_id(self, scorer, mock_fact_repo):
        """Test scoring with repo but no company_id."""
        financials = FinancialMetric(revenue=1000000)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id=None)

        assert 0 <= score <= 10
        mock_fact_repo.get_company_facts.assert_not_called()

    def test_merge_facts_revenue_growth(self, scorer, mock_fact_repo):
        """Test merging revenue growth fact into financials."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="revenue_growth_yoy",
                value=30,
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(growth_rate=10, employees=1)  # Original: 10%

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        assert score > 1.4

    def test_merge_facts_multiple_metrics(self, scorer, mock_fact_repo):
        """Test merging multiple facts into financials."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=5000000,
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="revenue_growth_yoy",
                value=25,
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="employee_count",
                value=100,
                confidence=0.90,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="gross_margin",
                value=60,
                confidence=0.85,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # Score should incorporate all facts
        assert score > 5.0  # Strong company with growth + profitability

    def test_merge_facts_repo_error(self, scorer, mock_fact_repo):
        """Test scoring handles repository errors gracefully."""
        mock_fact_repo.get_company_facts.side_effect = Exception("DB error")

        financials = FinancialMetric(revenue=1000000, growth_rate=15)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # Should still score based on original financials
        assert 0 <= score <= 10

    def test_confidence_to_level_high(self, scorer):
        """Test confidence conversion for high confidence."""
        level = confidence_to_level(0.95)
        assert level == ConfidenceLevel.CONFIRMED

    def test_confidence_to_level_medium(self, scorer):
        """Test confidence conversion for medium confidence."""
        level = confidence_to_level(0.80)
        assert level == ConfidenceLevel.ESTIMATED

    def test_confidence_to_level_low(self, scorer):
        """Test confidence conversion for low confidence."""
        level = confidence_to_level(0.60)
        assert level == ConfidenceLevel.UNKNOWN

    def test_confidence_to_level_unknown(self, scorer):
        """Test confidence conversion for unknown confidence."""
        level = confidence_to_level(0.30)
        assert level == ConfidenceLevel.UNKNOWN

    def test_confidence_to_level_boundaries(self, scorer):
        """Test confidence conversion at boundaries."""
        assert confidence_to_level(0.90) == ConfidenceLevel.CONFIRMED
        assert confidence_to_level(0.89) == ConfidenceLevel.ESTIMATED
        assert confidence_to_level(0.70) == ConfidenceLevel.ESTIMATED
        assert confidence_to_level(0.69) == ConfidenceLevel.UNKNOWN
        assert confidence_to_level(0.50) == ConfidenceLevel.UNKNOWN
        assert confidence_to_level(0.49) == ConfidenceLevel.UNKNOWN

    def test_score_with_high_growth_fact(self, scorer, mock_fact_repo):
        """Test scoring with high growth fact (30% YoY)."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="revenue_growth_yoy",
                value=30,
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        assert score > 1.4
        # Should have revenue growth component
        assert any(c.name == "Revenue Growth" for c in explanation.components)

    def test_score_with_profitability_fact(self, scorer, mock_fact_repo):
        """Test scoring with profitability fact."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="gross_margin",
                value=70,
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        assert score >= 1.0
        # Should have profitability component
        assert any(c.name == "Profitability Profile" for c in explanation.components)

    def test_score_with_funding_fact(self, scorer, mock_fact_repo):
        """Test scoring with funding fact."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="total_funding_raised",
                value=50000000,  # EUR 50M
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        assert score >= 1.0
        # Should have funding momentum component
        assert any(c.name == "Funding Momentum" for c in explanation.components)

    def test_score_with_efficiency_fact(self, scorer, mock_fact_repo):
        """Test scoring with employee efficiency (revenue per employee)."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=25000000,  # EUR 25M (500K per employee)
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="employee_count",
                value=50,  # 50 employees
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        assert score >= 1.0
        # Should have employee efficiency component
        assert any(c.name == "Employee Efficiency" for c in explanation.components)

    def test_score_ignores_unknown_fact_types(self, scorer, mock_fact_repo):
        """Test that unknown fact types are ignored."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="unknown_metric",
                value=100,
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # Should score without error, ignoring unknown fact
        assert 0 <= score <= 10

    def test_score_with_null_fact_values(self, scorer, mock_fact_repo):
        """Test that facts with null values are ignored."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="revenue_growth_yoy",
                value=None,  # Null value
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(growth_rate=15, employees=1)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # Should use original growth_rate (15%), not null fact
        assert 0 <= score <= 10
