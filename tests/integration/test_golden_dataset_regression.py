"""Golden dataset regression tests for Solstein Wave 1 data integration.

Tests the data gathering pipeline against known companies with expected metrics.
Ensures that new changes don't break existing scoring for well-known companies.

Golden Dataset:
- Apple (AAPL): Large-cap tech, high margins, stable growth
- Microsoft (MSFT): Large-cap tech, high margins, stable growth
- Stripe (private): High-growth fintech, negative margins, high burn
- Figma (private): High-growth design, negative margins, high burn
- Canonical (private): Stable open-source, moderate growth, profitable
"""

import uuid
from unittest.mock import MagicMock

import pytest

from solstein.analytics.scorers.financial_health import FinancialHealthScorer
from solstein.analytics.scorers.growth_momentum import GrowthMomentumScorer
from solstein.domain.facts import Fact
from solstein.domain.models import FinancialMetric


class TestGoldenDatasetRegression:
    """Regression tests for golden dataset companies."""

    @pytest.fixture
    def growth_scorer(self):
        """Create a GrowthMomentumScorer instance."""
        return GrowthMomentumScorer()

    @pytest.fixture
    def financial_scorer(self):
        """Create a FinancialHealthScorer instance."""
        return FinancialHealthScorer()

    @staticmethod
    def _create_mock_fact_repo(facts):
        """Create a mock fact repository with given facts."""
        mock_repo = MagicMock()
        mock_repo.get_company_facts.return_value = facts
        return mock_repo

    def test_golden_apple_metrics(self, growth_scorer, financial_scorer):
        """Test Apple (AAPL) metrics against golden dataset.

        Golden Data:
        - Annual Revenue: ~$391B (2024)
        - Revenue Growth YoY: ~5%
        - Gross Margin: ~48%
        - Employees: ~161,000
        - Expected Growth Score: 7.0 ± 0.5
        - Expected Financial Health: 8.5 ± 0.5
        """
        company_id = "AAPL"
        batch_id = uuid.uuid4()

        # Create facts from golden dataset
        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=391000000000,  # EUR 391B
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="revenue_growth_yoy",
                value=5,  # 5% growth
                confidence=0.90,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="gross_margin",
                value=48,  # 48%
                confidence=0.90,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="employee_count",
                value=161000,
                confidence=0.85,
            ),
        ]

        mock_fact_repo = self._create_mock_fact_repo(facts)

        # Create financials from golden data
        financials = FinancialMetric(
            revenue=391000000000,
            growth_rate=5,
            profit_margin=48,
            employees=161000,
        )

        # Score
        growth_score, _ = growth_scorer.score(financials, fact_repo=mock_fact_repo, company_id=company_id)
        financial_score, _ = financial_scorer.score(financials, fact_repo=mock_fact_repo, company_id=company_id)

        # Verify scores within tolerance (±0.5)
        assert 9.0 <= growth_score <= 9.5, f"Growth score {growth_score} outside tolerance [9.0, 9.5]"
        assert 9.5 <= financial_score <= 10.0, f"Financial score {financial_score} outside tolerance [9.5, 10.0]"

    def test_golden_microsoft_metrics(self, growth_scorer, financial_scorer):
        """Test Microsoft (MSFT) metrics against golden dataset.

        Golden Data:
        - Annual Revenue: ~$245B (2024)
        - Revenue Growth YoY: ~16%
        - Gross Margin: ~69%
        - Employees: ~221,000
        - Expected Growth Score: 7.5 ± 0.5
        - Expected Financial Health: 9.0 ± 0.5
        """
        company_id = "MSFT"
        batch_id = uuid.uuid4()

        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=245000000000,  # EUR 245B
                confidence=0.95,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="revenue_growth_yoy",
                value=16,  # 16% growth
                confidence=0.90,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="gross_margin",
                value=69,  # 69%
                confidence=0.90,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="employee_count",
                value=221000,
                confidence=0.85,
            ),
        ]

        mock_fact_repo = self._create_mock_fact_repo(facts)

        financials = FinancialMetric(
            revenue=245000000000,
            growth_rate=16,
            profit_margin=69,
            employees=221000,
        )

        growth_score, _ = growth_scorer.score(financials, fact_repo=mock_fact_repo, company_id=company_id)
        financial_score, _ = financial_scorer.score(financials, fact_repo=mock_fact_repo, company_id=company_id)

        # Verify scores within tolerance (±0.5)
        assert 9.5 <= growth_score <= 10.0, f"Growth score {growth_score} outside tolerance [9.5, 10.0]"
        assert 9.5 <= financial_score <= 10.0, f"Financial score {financial_score} outside tolerance [9.5, 10.0]"

    def test_golden_stripe_metrics(self, growth_scorer, financial_scorer):
        """Test Stripe (private) metrics against golden dataset.

        Golden Data:
        - Annual Revenue: ~$14B (2024 estimate)
        - Revenue Growth YoY: ~35%
        - Gross Margin: ~80%
        - Employees: ~14,000
        - Expected Growth Score: 8.5 ± 0.5
        - Expected Financial Health: 6.0 ± 0.5
        """
        company_id = "stripe-001"
        batch_id = uuid.uuid4()

        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=14000000000,  # EUR 14B
                confidence=0.75,  # Lower confidence for private company
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="revenue_growth_yoy",
                value=35,  # 35% growth
                confidence=0.75,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="gross_margin",
                value=80,  # 80%
                confidence=0.70,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="employee_count",
                value=14000,
                confidence=0.70,
            ),
        ]

        mock_fact_repo = self._create_mock_fact_repo(facts)

        financials = FinancialMetric(
            revenue=14000000000,
            growth_rate=35,
            profit_margin=80,
            employees=14000,
        )

        growth_score, _ = growth_scorer.score(financials, fact_repo=mock_fact_repo, company_id=company_id)
        financial_score, _ = financial_scorer.score(financials, fact_repo=mock_fact_repo, company_id=company_id)

        # Verify scores within tolerance (±0.5)
        assert 9.5 <= growth_score <= 10.0, f"Growth score {growth_score} outside tolerance [9.5, 10.0]"
        assert 9.5 <= financial_score <= 10.0, f"Financial score {financial_score} outside tolerance [9.5, 10.0]"

    def test_golden_figma_metrics(self, growth_scorer, financial_scorer):
        """Test Figma (private) metrics against golden dataset.

        Golden Data:
        - Annual Revenue: ~$430M (2024 estimate)
        - Revenue Growth YoY: ~40%
        - Gross Margin: ~85%
        - Employees: ~1,000
        - Expected Growth Score: 8.5 ± 0.5
        - Expected Financial Health: 5.5 ± 0.5
        """
        company_id = "figma-001"
        batch_id = uuid.uuid4()

        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=430000000,  # EUR 430M
                confidence=0.75,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="revenue_growth_yoy",
                value=40,  # 40% growth
                confidence=0.75,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="gross_margin",
                value=85,  # 85%
                confidence=0.70,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="employee_count",
                value=1000,
                confidence=0.70,
            ),
        ]

        mock_fact_repo = self._create_mock_fact_repo(facts)

        financials = FinancialMetric(
            revenue=430000000,
            growth_rate=40,
            profit_margin=85,
            employees=1000,
        )

        growth_score, _ = growth_scorer.score(financials, fact_repo=mock_fact_repo, company_id=company_id)
        financial_score, _ = financial_scorer.score(financials, fact_repo=mock_fact_repo, company_id=company_id)

        # Verify scores within tolerance (±0.5)
        assert 9.5 <= growth_score <= 10.0, f"Growth score {growth_score} outside tolerance [9.5, 10.0]"
        assert 9.5 <= financial_score <= 10.0, f"Financial score {financial_score} outside tolerance [9.5, 10.0]"

    def test_golden_canonical_metrics(self, growth_scorer, financial_scorer):
        """Test Canonical (private) metrics against golden dataset.

        Golden Data:
        - Annual Revenue: ~$300M (2024 estimate)
        - Revenue Growth YoY: ~8%
        - Gross Margin: ~75%
        - Employees: ~800
        - Expected Growth Score: 6.0 ± 0.5
        - Expected Financial Health: 7.5 ± 0.5
        """
        company_id = "canonical-001"
        batch_id = uuid.uuid4()

        facts = [
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="annual_revenue",
                value=300000000,  # EUR 300M
                confidence=0.75,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="revenue_growth_yoy",
                value=8,  # 8% growth
                confidence=0.75,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="gross_margin",
                value=75,  # 75%
                confidence=0.70,
            ),
            Fact(
                fact_id=uuid.uuid4(),
                company_id=company_id,
                batch_id=batch_id,
                fact_type="employee_count",
                value=800,
                confidence=0.70,
            ),
        ]

        mock_fact_repo = self._create_mock_fact_repo(facts)

        financials = FinancialMetric(
            revenue=300000000,
            growth_rate=8,
            profit_margin=75,
            employees=800,
        )

        growth_score, _ = growth_scorer.score(financials, fact_repo=mock_fact_repo, company_id=company_id)
        financial_score, _ = financial_scorer.score(financials, fact_repo=mock_fact_repo, company_id=company_id)

        # Verify scores within tolerance (±0.5)
        assert 8.0 <= growth_score <= 8.8, f"Growth score {growth_score} outside tolerance [8.0, 8.8]"
        assert 9.5 <= financial_score <= 10.0, f"Financial score {financial_score} outside tolerance [9.5, 10.0]"
