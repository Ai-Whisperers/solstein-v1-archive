"""Unit tests for FinancialHealthScorer with facts integration.

Tests cover:
- Financial health scoring with facts from repository
- Fact merging into financial metrics
- Confidence level conversion
- Backward compatibility with existing scoring
"""

import uuid
from unittest.mock import MagicMock

import pytest

from solstein.analytics.scorers._shared import confidence_to_level
from solstein.analytics.scorers.financial_health import FinancialHealthScorer
from solstein.domain.facts import Fact
from solstein.domain.models import ConfidenceLevel, FinancialMetric


class TestFinancialHealthScorerWithFacts:
    """Tests for financial health scorer with facts integration."""

    @pytest.fixture
    def scorer(self):
        """Create a FinancialHealthScorer instance."""
        return FinancialHealthScorer()

    @pytest.fixture
    def mock_fact_repo(self):
        """Create a mock FactRepository."""
        return MagicMock()

    def test_score_without_facts(self, scorer):
        """Test scoring works without facts (backward compatibility)."""
        financials = FinancialMetric(
            revenue=5000000,
            profit_margin=20,
            employees=50,
            funding_raised=10000000,
        )

        score, explanation = scorer.score(financials)

        assert 0 <= score <= 10
        assert explanation.final_score == score
        assert len(explanation.components) > 0

    def test_score_with_facts_no_repo(self, scorer):
        """Test scoring with facts parameter but no repo provided."""
        financials = FinancialMetric(revenue=5000000)

        score, explanation = scorer.score(financials, fact_repo=None, company_id="test-company")

        assert 0 <= score <= 10

    def test_score_with_facts_no_company_id(self, scorer, mock_fact_repo):
        """Test scoring with repo but no company_id."""
        financials = FinancialMetric(revenue=5000000)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id=None)

        assert 0 <= score <= 10
        mock_fact_repo.get_company_facts.assert_not_called()

    def test_merge_facts_revenue(self, scorer, mock_fact_repo):
        """Test merging revenue fact into financials."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=11000000,  # EUR 11M
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(revenue=1000000)  # Original: EUR 1M

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # Score should reflect EUR 10M revenue (from fact), not EUR 1M
        assert score >= 3.0  # Large revenue should give good score

    def test_merge_facts_multiple_metrics(self, scorer, mock_fact_repo):
        """Test merging multiple facts into financials."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=11000000,  # EUR 11M
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="gross_margin",
                value=50,  # 50%
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
                fact_type="total_funding_raised",
                value=5000000,  # EUR 5M
                confidence=0.85,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # Score should incorporate all facts
        assert score > 5.0  # Healthy company with good metrics

    def test_merge_facts_repo_error(self, scorer, mock_fact_repo):
        """Test scoring handles repository errors gracefully."""
        mock_fact_repo.get_company_facts.side_effect = Exception("DB error")

        financials = FinancialMetric(revenue=5000000, profit_margin=15)

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

    def test_score_healthy_company(self, scorer, mock_fact_repo):
        """Test scoring healthy company (24mo runway + profitable)."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=11000000,  # EUR 11M
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="gross_margin",
                value=70,  # 70% margin
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="total_funding_raised",
                value=20000000,  # EUR 20M (2x revenue)
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # Healthy company should score > 6.0
        assert score > 6.0
        # Should have multiple positive components
        assert len(explanation.components) >= 2

    def test_score_struggling_company(self, scorer, mock_fact_repo):
        """Test scoring struggling company (low runway, unprofitable)."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=500000,  # EUR 500K
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="gross_margin",
                value=-10,  # -10% margin (unprofitable)
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="total_funding_raised",
                value=100000,  # EUR 100K (0.2x revenue)
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # Struggling company should score <= 4.0
        assert score <= 4.0

    def test_score_with_profitability_fact(self, scorer, mock_fact_repo):
        """Test scoring with profitability fact."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="gross_margin",
                value=60,  # 60% margin
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # High profitability should boost score
        assert score >= 3.0
        # Should have profitability component
        assert any(c.name == "Profitability Health" for c in explanation.components)

    def test_score_with_efficiency_fact(self, scorer, mock_fact_repo):
        """Test scoring with employee efficiency (revenue per employee)."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=25000000,  # EUR 25M
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="employee_count",
                value=40,  # EUR 625K per employee (> 500K threshold)
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # EUR 625K per employee is good efficiency
        assert score > 4.0
        # Should have efficiency component
        assert any(c.name == "Operating Efficiency" for c in explanation.components)

    def test_score_with_funding_cushion_fact(self, scorer, mock_fact_repo):
        """Test scoring with funding cushion (funding vs revenue ratio)."""
        batch_id = uuid.uuid4()
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=5000000,  # EUR 5M
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id="test-company",
                batch_id=batch_id,
                fact_type="total_funding_raised",
                value=25000000,  # EUR 25M (5x revenue)
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(allow_empty_primary=True)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # High funding cushion should boost score
        assert score > 4.0
        # Should have funding cushion component
        assert any(c.name == "Funding Cushion" for c in explanation.components)

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
                fact_type="annual_revenue",
                value=None,  # Null value
                confidence=0.95,
            ),
        ]
        mock_fact_repo.get_company_facts.return_value = facts

        financials = FinancialMetric(revenue=5000000)

        score, explanation = scorer.score(financials, fact_repo=mock_fact_repo, company_id="test-company")

        # Should use original revenue (EUR 5M), not null fact
        assert 0 <= score <= 10
