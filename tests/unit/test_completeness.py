"""
Task 3: Unit Tests for Data Completeness Scoring

Tests the completeness calculator for scoring and tier assignment.
"""


from solstein.analytics.completeness import CompletenessCalculator, DataQualityTier
from solstein.domain.models import AIMaturity, Company, CompanyTier, FinancialMetric
from tests.factories import make_company, make_financial_metric


class TestCompletenessCalculator:
    """Test CompletenessCalculator."""

    def test_calculator_initializes(self):
        """Calculator should initialize successfully."""
        calc = CompletenessCalculator()
        assert calc is not None
        assert len(calc.TRACKED_FIELDS) == 19

    def test_score_calculation(self):
        """Score should be between 0 and 100."""
        calc = CompletenessCalculator()
        company = make_company(id="test-1")
        score = calc.calculate_completeness_score(company)
        assert 0 <= score <= 100
        assert score == round(score, 1)

    def test_tier_assignment_complete(self):
        """Score 80% should be COMPLETE tier."""
        calc = CompletenessCalculator()
        assert calc.assign_tier(80.0) == DataQualityTier.COMPLETE
        assert calc.assign_tier(100.0) == DataQualityTier.COMPLETE

    def test_tier_assignment_partial(self):
        """Score 50-79% should be PARTIAL tier."""
        calc = CompletenessCalculator()
        assert calc.assign_tier(50.0) == DataQualityTier.PARTIAL
        assert calc.assign_tier(79.0) == DataQualityTier.PARTIAL

    def test_tier_assignment_minimal(self):
        """Score 20-49% should be MINIMAL tier."""
        calc = CompletenessCalculator()
        assert calc.assign_tier(20.0) == DataQualityTier.MINIMAL
        assert calc.assign_tier(49.0) == DataQualityTier.MINIMAL

    def test_tier_assignment_insufficient(self):
        """Score 0-19% should be INSUFFICIENT tier."""
        calc = CompletenessCalculator()
        assert calc.assign_tier(0.0) == DataQualityTier.INSUFFICIENT
        assert calc.assign_tier(19.0) == DataQualityTier.INSUFFICIENT

    def test_completeness_report(self):
        """Report should include all required fields."""
        calc = CompletenessCalculator()
        company = make_company(id="test-1", name="Test Corp")
        report = calc.get_completeness_report(company)

        assert report["company_id"] == "test-1"
        assert report["company_name"] == "Test Corp"
        assert "completeness_score" in report
        assert "data_quality_tier" in report
        assert "total_tracked_fields" in report
        assert "non_null_fields" in report
        assert "field_details" in report
        assert len(report["field_details"]) == 19

    def test_field_extraction_financial(self):
        """Should extract financial fields correctly."""
        calc = CompletenessCalculator()
        company = make_company(
            id="test-1",
            financials=make_financial_metric(revenue=100.0),
        )
        assert calc._get_field_value(company, "revenue") == 100.0

    def test_field_extraction_company_attribute(self):
        """Should extract company attributes correctly."""
        calc = CompletenessCalculator()
        company = make_company(
            id="test-1",
            tier=CompanyTier.TIER_2,
            ai_maturity=AIMaturity.STRONG,
        )
        assert calc._get_field_value(company, "tier") == CompanyTier.TIER_2
        assert calc._get_field_value(company, "ai_maturity") == AIMaturity.STRONG

    def test_global_instance(self):
        """Global instance should exist."""
        from solstein.analytics.completeness import completeness_calculator
        assert completeness_calculator is not None
        assert isinstance(completeness_calculator, CompletenessCalculator)

    def test_partial_company_scenario(self):
        """Partial company with 13/19 fields should score ~68%."""
        calc = CompletenessCalculator()
        company = make_company(
            id="partial-1",
            tier=CompanyTier.TIER_2,
            ai_maturity=AIMaturity.MODERATE,
            ai_score=7,
            ai_signal_level="High",
            ai_key_capabilities="ML",
            ai_in_production=True,
            financials=make_financial_metric(
                revenue=100.0,
                growth_rate=15.0,
                employees=50,
                profit_margin=10.0,
                funding_raised=50.0,
            ),
        )
        score = calc.calculate_completeness_score(company)
        tier = calc.assign_tier(score)

        assert 50 <= score < 80
        assert tier == DataQualityTier.PARTIAL

    def test_minimal_company_scenario(self):
        """Minimal company with few fields should score 20-49%."""
        calc = CompletenessCalculator()
        company = make_company(
            id="minimal-1",
            tier=CompanyTier.TIER_3,
            financials=make_financial_metric(
                revenue=100.0,
                growth_rate=None,
                employees=None,
            ),
        )
        score = calc.calculate_completeness_score(company)
        tier = calc.assign_tier(score)

        assert 20 <= score < 50
        assert tier == DataQualityTier.MINIMAL

    def test_insufficient_company_scenario(self):
        """Insufficient company with minimal fields."""
        calc = CompletenessCalculator()
        company = Company(
            id="insufficient-1",
            name="Insufficient Corp",
            financials=FinancialMetric(),
        )
        score = calc.calculate_completeness_score(company)
        tier = calc.assign_tier(score)

        assert 15 <= score < 50
        assert tier in [DataQualityTier.INSUFFICIENT, DataQualityTier.MINIMAL]
