"""
Task 18: Eneve Consistency Validation

Validates that Eneve analysis produces consistent scores across multiple runs.
Ensures deterministic scoring with variance < 0.2 for all dimensions.
"""

import pytest
from solstein.domain.models import Company, FinancialMetric, AIMaturity
from solstein.analytics.scoring import GrowthScorer
from tests.data_quality.golden_dataset import get_golden_company_by_name


class TestEnevelConsistencyValidation:
    """Test Eneve consistency across multiple runs."""

    @pytest.fixture
    def eneve_company(self):
        """Create Eneve company for testing."""
        return Company(
            id="eneve-1",
            name="Eneve",
            industry="Energy Software",
            headquarters="London",
            description="AI-powered energy optimization platform",
            composite_score=7.5,
            classification="Phoenix",
            financials=FinancialMetric(
                revenue=50,
                growth_rate=80,
                employees=120,
                profit_margin=15,
                funding_raised=25,
                revenue_confidence="Confirmed",
                employees_confidence="Confirmed",
                growth_confidence="Confirmed",
            ),
            revenue_timeline=[
                {"year": "2024", "eur_millions": 50, "yoy_growth_pct": 80, "confidence": "Confirmed"},
                {"year": "2023", "eur_millions": 28, "yoy_growth_pct": 75, "confidence": "Confirmed"},
                {"year": "2022", "eur_millions": 16, "yoy_growth_pct": 60, "confidence": "Confirmed"},
            ],
            ebitda_margin=12,
            recurring_revenue_pct=75,
            revenue_per_employee_eur_k=417,
            ai_maturity=AIMaturity.STRONG,
            ai_score=8,
            saas_maturity=8,
            total_funding_raised_eur=25,
            lead_investors=["Pale Blue Dot", "Lowercarbon Capital"],
            key_customers=["Shell", "BP", "Equinor"],
            geographic_presence=["UK", "Netherlands", "Germany"],
        )

    def test_eneve_consistency_single_run(self, eneve_company):
        """Single run should produce valid scores."""
        scorer = GrowthScorer()
        result = scorer.calculate_scores(eneve_company)

        assert result.composite_score is not None
        assert result.growth_score is not None
        assert result.financial_health_score is not None
        assert result.competitive_position_score is not None
        assert 0 <= result.composite_score <= 10
        assert 0 <= result.growth_score <= 10
        assert 0 <= result.financial_health_score <= 10
        assert 0 <= result.competitive_position_score <= 10

    def test_eneve_consistency_multiple_runs(self, eneve_company):
        """Multiple runs should produce consistent scores."""
        scorer = GrowthScorer()
        num_runs = 10

        # Run scoring 10 times
        results = []
        for _ in range(num_runs):
            # Create fresh copy for each run
            company_copy = Company(**eneve_company.model_dump())
            result = scorer.calculate_scores(company_copy)
            results.append(result)

        # Extract scores
        composite_scores = [r.composite_score for r in results]
        growth_scores = [r.growth_score for r in results]
        financial_health_scores = [r.financial_health_score for r in results]
        competitive_position_scores = [r.competitive_position_score for r in results]

        # Calculate variance (max - min)
        composite_variance = max(composite_scores) - min(composite_scores)
        growth_variance = max(growth_scores) - min(growth_scores)
        financial_health_variance = max(financial_health_scores) - min(financial_health_scores)
        competitive_position_variance = max(competitive_position_scores) - min(competitive_position_scores)

        # Verify variance < 0.2 for all dimensions
        assert composite_variance < 0.2, f"Composite score variance {composite_variance} exceeds 0.2"
        assert growth_variance < 0.2, f"Growth score variance {growth_variance} exceeds 0.2"
        assert financial_health_variance < 0.2, f"Financial health variance {financial_health_variance} exceeds 0.2"
        assert competitive_position_variance < 0.2, (
            f"Competitive position variance {competitive_position_variance} exceeds 0.2"
        )

    def test_eneve_consistency_classification_stable(self, eneve_company):
        """Classification should remain stable across runs."""
        scorer = GrowthScorer()
        num_runs = 10

        classifications = []
        for _ in range(num_runs):
            company_copy = Company(**eneve_company.model_dump())
            result = scorer.calculate_scores(company_copy)
            classifications.append(result.classification)

        # All classifications should be the same
        assert len(set(classifications)) == 1, f"Classifications vary: {set(classifications)}"
        assert classifications[0] == "Phoenix"

    def test_eneve_consistency_deterministic(self, eneve_company):
        """Scoring should be deterministic (same input = same output)."""
        scorer = GrowthScorer()

        # Score the same company twice
        company_copy1 = Company(**eneve_company.model_dump())
        company_copy2 = Company(**eneve_company.model_dump())
        result1 = scorer.calculate_scores(company_copy1)
        result2 = scorer.calculate_scores(company_copy2)

        # Scores should be identical
        assert result1.composite_score == result2.composite_score
        assert result1.growth_score == result2.growth_score
        assert result1.financial_health_score == result2.financial_health_score
        assert result1.competitive_position_score == result2.competitive_position_score
        assert result1.classification == result2.classification

    def test_eneve_consistency_no_randomness(self, eneve_company):
        """Scoring should not use randomness."""
        scorer = GrowthScorer()

        # Run 20 times and check for any variation
        scores = []
        for _ in range(20):
            company_copy = Company(**eneve_company.model_dump())
            result = scorer.calculate_scores(company_copy)
            scores.append(result.composite_score)

        # All scores should be identical
        assert len(set(scores)) == 1, f"Scores vary: {set(scores)}"

    def test_eneve_consistency_reproducible(self, eneve_company):
        """Results should be reproducible across different scorer instances."""
        # Create two separate scorer instances
        scorer1 = GrowthScorer()
        scorer2 = GrowthScorer()

        company_copy1 = Company(**eneve_company.model_dump())
        company_copy2 = Company(**eneve_company.model_dump())
        result1 = scorer1.calculate_scores(company_copy1)
        result2 = scorer2.calculate_scores(company_copy2)

        # Results should be identical
        assert result1.composite_score == result2.composite_score
        assert result1.growth_score == result2.growth_score
        assert result1.financial_health_score == result2.financial_health_score
        assert result1.competitive_position_score == result2.competitive_position_score

    def test_eneve_consistency_within_golden_range(self, eneve_company):
        """Eneve scores should be within golden dataset expectations."""
        scorer = GrowthScorer()
        company_copy = Company(**eneve_company.model_dump())
        result = scorer.calculate_scores(company_copy)

        # Get golden expectations
        golden = get_golden_company_by_name("Eneve")
        assert golden is not None

        # Verify within expected ranges
        assert golden.validate_composite_score(result.composite_score)
        assert golden.validate_growth_score(result.growth_score)
        assert golden.validate_financial_health_score(result.financial_health_score)
        assert golden.validate_competitive_position_score(result.competitive_position_score)
        assert golden.validate_classification(result.classification)

    def test_eneve_consistency_variance_calculation(self, eneve_company):
        """Variance calculation should be correct."""
        scorer = GrowthScorer()
        num_runs = 10

        scores = []
        for _ in range(num_runs):
            company_copy = Company(**eneve_company.model_dump())
            result = scorer.calculate_scores(company_copy)
            scores.append(result.composite_score)

        # Calculate variance
        variance = max(scores) - min(scores)

        # Verify calculation
        assert variance >= 0
        assert variance < 0.2

    def test_eneve_consistency_all_dimensions(self, eneve_company):
        """All scoring dimensions should be consistent."""
        scorer = GrowthScorer()
        num_runs = 5

        # Run multiple times
        results = []
        for _ in range(num_runs):
            company_copy = Company(**eneve_company.model_dump())
            result = scorer.calculate_scores(company_copy)
            results.append(result)

        # Check each dimension
        for i in range(1, num_runs):
            assert results[i].composite_score == results[0].composite_score
            assert results[i].growth_score == results[0].growth_score
            assert results[i].financial_health_score == results[0].financial_health_score
            assert results[i].competitive_position_score == results[0].competitive_position_score

    def test_eneve_consistency_scoring_breakdown(self, eneve_company):
        """Scoring breakdown should be consistent."""
        scorer = GrowthScorer()

        company_copy1 = Company(**eneve_company.model_dump())
        company_copy2 = Company(**eneve_company.model_dump())
        result1 = scorer.calculate_scores(company_copy1)
        result2 = scorer.calculate_scores(company_copy2)

        # Scoring breakdowns should be identical
        assert result1.scoring_breakdown == result2.scoring_breakdown
