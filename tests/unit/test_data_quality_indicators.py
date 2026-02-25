"""
Task 14: Data Quality Indicators - Test Suite

Tests for data quality indicators, provenance tracking, and confidence levels.
"""

import pytest
from solstein.presentation.data_quality_indicators import DataQualityIndicators
from solstein.domain.models import Company, FinancialMetric, ConfidenceLevel, CompanyTier
from solstein.analytics.completeness import DataQualityTier


class TestDataQualityIndicators:
    """Test data quality indicators and provenance."""

    @pytest.fixture
    def sparse_company(self):
        """Company with sparse data."""
        return Company(
            id="sparse-1",
            name="Sparse Company",
            industry="Energy Software",
            headquarters="London",
            composite_score=5.5,
            classification="Salt",
            financials=FinancialMetric(
                revenue=None,
                employees=None,
            ),
        )

    @pytest.fixture
    def moderate_company(self):
        """Company with moderate data."""
        return Company(
            id="moderate-1",
            name="Moderate Company",
            industry="Energy Software",
            headquarters="Berlin",
            composite_score=6.5,
            classification="Salt",
            financials=FinancialMetric(
                revenue=100,
                growth_rate=25,
                employees=150,
                profit_margin=12,
                funding_raised=50,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
                employees_confidence=ConfidenceLevel.CONFIRMED,
                growth_confidence=ConfidenceLevel.ESTIMATED,
                funding_confidence=ConfidenceLevel.ESTIMATED,
            ),
            ebitda_margin=15,
            recurring_revenue_pct=60,
            revenue_per_employee_eur_k=667,
            ai_maturity="Strong",
            ai_score=6,
            threat_level="Medium",
            geographic_presence=["Germany", "Austria"],
        )

    @pytest.fixture
    def rich_company(self):
        """Company with rich data."""
        return Company(
            id="rich-1",
            name="Rich Company",
            industry="Energy Software",
            headquarters="Amsterdam",
            composite_score=7.5,
            classification="Phoenix",
            financials=FinancialMetric(
                revenue=250,
                growth_rate=60,
                employees=500,
                profit_margin=20,
                funding_raised=150,
                valuation=1000,
                revenue_confidence=ConfidenceLevel.CONFIRMED,
                employees_confidence=ConfidenceLevel.CONFIRMED,
                growth_confidence=ConfidenceLevel.CONFIRMED,
                funding_confidence=ConfidenceLevel.CONFIRMED,
                valuation_confidence=ConfidenceLevel.ESTIMATED,
            ),
            ebitda_margin=25,
            recurring_revenue_pct=85,
            revenue_per_employee_eur_k=500,
            employee_cagr_3yr=35,
            open_positions=50,
            ai_score=8,
            ai_maturity="Very Strong",
            ai_signal_level="High",
            ai_key_capabilities="LLM, RAG, Agents",
            ai_in_production=True,
            threat_level="Low",
            tier=CompanyTier.TIER_1,
            saas_maturity=9,
            total_funding_raised_eur=150,
            lead_investors=["Accel", "Sequoia"],
            key_customers=["Shell", "BP"],
            geographic_presence=["Netherlands", "Belgium", "Germany"],
        )

    def test_completeness_score_sparse(self, sparse_company):
        """Sparse company should have low completeness score."""
        score = DataQualityIndicators.get_completeness_score(sparse_company)
        assert score < 40

    def test_completeness_score_moderate(self, moderate_company):
        """Moderate company should have medium completeness score."""
        score = DataQualityIndicators.get_completeness_score(moderate_company)
        assert 40 <= score < 80

    def test_completeness_score_rich(self, rich_company):
        """Rich company should have high completeness score."""
        score = DataQualityIndicators.get_completeness_score(rich_company)
        assert score >= 70

    def test_data_quality_tier_sparse(self, sparse_company):
        """Sparse company should have MINIMAL or INSUFFICIENT tier."""
        tier = DataQualityIndicators.get_data_quality_tier(sparse_company)
        assert tier in [DataQualityTier.MINIMAL, DataQualityTier.INSUFFICIENT]

    def test_data_quality_tier_moderate(self, moderate_company):
        """Moderate company should have PARTIAL tier."""
        tier = DataQualityIndicators.get_data_quality_tier(moderate_company)
        assert tier == DataQualityTier.PARTIAL

    def test_data_quality_tier_rich(self, rich_company):
        """Rich company should have PARTIAL or COMPLETE tier."""
        tier = DataQualityIndicators.get_data_quality_tier(rich_company)
        assert tier in [DataQualityTier.PARTIAL, DataQualityTier.COMPLETE]

    def test_executive_summary_section_contains_score(self, moderate_company):
        """Executive summary should contain completeness score."""
        section = DataQualityIndicators.get_executive_summary_section(moderate_company)
        assert "Completeness Score" in section
        assert "%" in section
        assert "Tier" in section

    def test_executive_summary_section_contains_indicators(self, moderate_company):
        """Executive summary should explain confidence indicators."""
        section = DataQualityIndicators.get_executive_summary_section(moderate_company)
        assert "✓" in section
        assert "~" in section
        assert "?" in section

    def test_metric_with_indicator_confirmed(self):
        """Confirmed metric should have ✓ indicator."""
        result = DataQualityIndicators.get_metric_with_indicator(100, ConfidenceLevel.CONFIRMED)
        assert result.startswith("✓")
        assert "100" in result

    def test_metric_with_indicator_estimated(self):
        """Estimated metric should have ~ indicator."""
        result = DataQualityIndicators.get_metric_with_indicator(50.5, ConfidenceLevel.ESTIMATED)
        assert result.startswith("~")
        assert "50.5" in result

    def test_metric_with_indicator_unknown(self):
        """Unknown metric should have ? indicator."""
        result = DataQualityIndicators.get_metric_with_indicator(None, ConfidenceLevel.UNKNOWN)
        assert result.startswith("?")

    def test_metric_with_indicator_formats_float(self):
        """Float metrics should be formatted with one decimal."""
        result = DataQualityIndicators.get_metric_with_indicator(123.456, ConfidenceLevel.CONFIRMED)
        assert "123.5" in result

    def test_metric_with_indicator_formats_int(self):
        """Integer metrics should be formatted with commas."""
        result = DataQualityIndicators.get_metric_with_indicator(1000000, ConfidenceLevel.CONFIRMED)
        assert "1,000,000" in result

    def test_data_provenance_table_contains_metrics(self, moderate_company):
        """Provenance table should contain key metrics."""
        table = DataQualityIndicators.get_data_provenance_table(moderate_company)
        assert "| Metric | Value | Confidence | Source |" in table
        assert "Revenue" in table
        assert "Employees" in table

    def test_data_provenance_table_contains_indicators(self, moderate_company):
        """Provenance table should contain confidence indicators."""
        table = DataQualityIndicators.get_data_provenance_table(moderate_company)
        assert "✓" in table or "~" in table or "?" in table

    def test_data_quality_flags_sparse_warning(self, sparse_company):
        """Sparse company should have sparse data warning."""
        flags = DataQualityIndicators.get_data_quality_flags(sparse_company)
        assert any("Sparse Data" in flag for flag in flags)

    def test_data_quality_flags_missing_revenue(self, sparse_company):
        """Company without revenue should have warning."""
        flags = DataQualityIndicators.get_data_quality_flags(sparse_company)
        assert any("Revenue" in flag for flag in flags)

    def test_data_quality_flags_missing_employees(self, sparse_company):
        """Company without employees should have warning."""
        flags = DataQualityIndicators.get_data_quality_flags(sparse_company)
        assert any("Employee" in flag for flag in flags)

    def test_data_quality_flags_contradiction_ai(self):
        """Company with contradictory AI data should have warning."""
        company = Company(
            id="contradiction-1",
            name="Contradiction Company",
            industry="Energy Software",
            ai_maturity="None",
            ai_score=8,  # Contradicts "None" maturity
            financials=FinancialMetric(revenue=100, employees=50),
        )
        flags = DataQualityIndicators.get_data_quality_flags(company)
        assert any("Contradiction" in flag for flag in flags)

    def test_data_quality_flags_multiple_estimates(self):
        """Company with multiple estimated metrics should have warning."""
        company = Company(
            id="estimates-1",
            name="Estimates Company",
            industry="Energy Software",
            financials=FinancialMetric(
                revenue=100,
                employees=50,
                growth_rate=25,
                revenue_confidence=ConfidenceLevel.ESTIMATED,
                employees_confidence=ConfidenceLevel.ESTIMATED,
                growth_confidence=ConfidenceLevel.ESTIMATED,
            ),
        )
        flags = DataQualityIndicators.get_data_quality_flags(company)
        assert any("Multiple Estimates" in flag for flag in flags)

    def test_data_confidence_section_contains_flags(self, sparse_company):
        """Data confidence section should contain quality flags."""
        section = DataQualityIndicators.get_data_confidence_section(sparse_company)
        assert "Quality Flags" in section
        assert "⚠️" in section

    def test_data_confidence_section_contains_provenance(self, moderate_company):
        """Data confidence section should contain provenance table."""
        section = DataQualityIndicators.get_data_confidence_section(moderate_company)
        assert "Data Sources & Confidence" in section
        assert "| Metric | Value | Confidence | Source |" in section

    def test_data_confidence_section_contains_guide(self, moderate_company):
        """Data confidence section should contain interpretation guide."""
        section = DataQualityIndicators.get_data_confidence_section(moderate_company)
        assert "Interpretation Guide" in section
        assert "Confirmed" in section
        assert "Estimated" in section
        assert "Unknown" in section

    def test_metric_confidence_summary_confirmed(self, moderate_company):
        """Confidence summary should show confirmed metrics."""
        summary = DataQualityIndicators.get_metric_confidence_summary(moderate_company)
        assert summary["Revenue"] == "✓"
        assert summary["Employees"] == "✓"

    def test_metric_confidence_summary_estimated(self, moderate_company):
        """Confidence summary should show estimated metrics."""
        summary = DataQualityIndicators.get_metric_confidence_summary(moderate_company)
        assert summary["Growth Rate"] == "~"

    def test_metric_confidence_summary_derived_metrics(self, moderate_company):
        """Confidence summary should show derived metrics as estimated."""
        summary = DataQualityIndicators.get_metric_confidence_summary(moderate_company)
        assert summary.get("EBITDA Margin") == "~"
        assert summary.get("Recurring Revenue %") == "~"

    def test_metric_confidence_summary_ai_metrics(self, moderate_company):
        """Confidence summary should include AI metrics."""
        summary = DataQualityIndicators.get_metric_confidence_summary(moderate_company)
        assert "AI Maturity" in summary
        assert "AI Score" in summary

    def test_all_companies_have_quality_assessment(self, sparse_company, moderate_company, rich_company):
        """All companies should have quality assessment."""
        for company in [sparse_company, moderate_company, rich_company]:
            score = DataQualityIndicators.get_completeness_score(company)
            assert 0 <= score <= 100
            tier = DataQualityIndicators.get_data_quality_tier(company)
            assert tier in [
                DataQualityTier.COMPLETE,
                DataQualityTier.PARTIAL,
                DataQualityTier.MINIMAL,
                DataQualityTier.INSUFFICIENT,
            ]

    def test_no_hidden_data_quality(self, sparse_company):
        """Data quality should never be hidden from users."""
        section = DataQualityIndicators.get_executive_summary_section(sparse_company)
        assert len(section) > 100  # Should have substantial content
        assert "Data Quality" in section or "Completeness" in section

    def test_sparse_data_not_shown_as_high_confidence(self, sparse_company):
        """Sparse data should not be shown as high confidence."""
        section = DataQualityIndicators.get_executive_summary_section(sparse_company)
        score = DataQualityIndicators.get_completeness_score(sparse_company)
        if score < 40:
            # Should not claim high confidence
            assert "high confidence" not in section.lower() or "limited" in section.lower()
