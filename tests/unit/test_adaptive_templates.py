"""
Task 13: Context-Aware Report Templates - Test Suite

Tests for adaptive report templates that respond to data availability and classification.
"""

import pytest

from solstein.domain.models import Company, FinancialMetric
from solstein.presentation.adaptive_templates import AdaptiveTemplates


class TestAdaptiveTemplates:
    """Test context-aware report template generation."""

    @pytest.fixture
    def sparse_company(self):
        """Company with sparse data (< 40% complete)."""
        return Company(
            id="sparse-1",
            name="Sparse Data Company",
            industry="Energy Software",
            headquarters="London",
            description="Test company with minimal data",
            composite_score=5.5,
            classification="Salt",
            # Only 2-3 fields set to keep completeness low (~10-15%)
            financials=FinancialMetric(
                revenue=None,
                employees=None,
                allow_empty_primary=True,
            ),
        )

    @pytest.fixture
    def moderate_company(self):
        """Company with moderate data (40-70% complete)."""
        return Company(
            id="moderate-1",
            name="Moderate Data Company",
            industry="Energy Software",
            headquarters="Berlin",
            description="Test company with moderate data",
            composite_score=6.5,
            classification="Salt",
            # Set ~10 of 19 tracked fields for ~50% completeness
            revenue_timeline=[
                {"year": "2024", "eur_millions": 100, "yoy_growth_pct": 25, "confidence": "Confirmed"},
                {"year": "2023", "eur_millions": 80, "yoy_growth_pct": 20, "confidence": "Confirmed"},
            ],
            financials=FinancialMetric(
                revenue=100,
                growth_rate=25,
                employees=150,
                profit_margin=12,
                ebitda_margin=15,
            ),
            ebitda_margin=15,
            recurring_revenue_pct=60,
            revenue_per_employee_eur_k=667,
            ai_maturity="Strong",
            ai_score=6,
            threat_level="Medium",
        )

    @pytest.fixture
    def rich_company(self):
        """Company with rich data (> 70% complete)."""
        return Company(
            id="rich-1",
            name="Rich Data Company",
            industry="Energy Software",
            headquarters="Amsterdam",
            description="Test company with comprehensive data",
            composite_score=7.5,
            classification="Phoenix",
            # Set ~16 of 19 tracked fields for ~85% completeness
            revenue_timeline=[
                {"year": "2024", "eur_millions": 250, "yoy_growth_pct": 60, "confidence": "Confirmed"},
                {"year": "2023", "eur_millions": 156, "yoy_growth_pct": 55, "confidence": "Confirmed"},
                {"year": "2022", "eur_millions": 100, "yoy_growth_pct": 50, "confidence": "Confirmed"},
            ],
            financials=FinancialMetric(
                revenue=250,
                growth_rate=60,
                employees=500,
                profit_margin=20,
                funding_raised=150,
                valuation=1000,
                ebitda_margin=25,
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
            saas_maturity=9,
            total_funding_raised_eur=150,
            lead_investors=["Accel", "Sequoia"],
            key_customers=["Shell", "BP", "Equinor"],
            geographic_presence=["UK", "Germany", "Netherlands"],
        )

    def test_sparse_strengths_never_empty(self, sparse_company):
        """Sparse data companies should still have strengths section."""
        strengths = AdaptiveTemplates.get_strengths_section(sparse_company)

        assert "## Identified Strengths" in strengths
        assert "Limited data available" in strengths
        assert len(strengths) > 100  # Should have meaningful content
        assert "No significant strengths identified" not in strengths

    def test_sparse_strengths_includes_score(self, sparse_company):
        """Sparse strengths should mention composite score."""
        strengths = AdaptiveTemplates.get_strengths_section(sparse_company)

        assert "Composite Positioning" in strengths or "Competitive Positioning" in strengths

    def test_moderate_strengths_includes_growth(self, moderate_company):
        """Moderate data should include growth metrics."""
        strengths = AdaptiveTemplates.get_strengths_section(moderate_company)

        assert "## Identified Strengths" in strengths
        assert "Growth" in strengths or "growth" in strengths
        assert "25" in strengths  # Should mention 25% growth

    def test_moderate_strengths_includes_profitability(self, moderate_company):
        """Moderate data should include profitability metrics."""
        strengths = AdaptiveTemplates.get_strengths_section(moderate_company)

        assert "Profitability" in strengths or "profitability" in strengths
        assert "15" in strengths  # Should mention 15% EBITDA margin

    def test_moderate_strengths_includes_ai(self, moderate_company):
        """Moderate data should include AI maturity."""
        strengths = AdaptiveTemplates.get_strengths_section(moderate_company)

        assert "AI" in strengths or "ai" in strengths.lower()

    def test_rich_strengths_detailed_analysis(self, rich_company):
        """Rich data should provide detailed analysis."""
        strengths = AdaptiveTemplates.get_strengths_section(rich_company)

        assert "## Identified Strengths" in strengths
        assert "Exceptional Growth" in strengths or "Strong Growth" in strengths
        assert "60" in strengths  # Should mention 60% growth
        assert "Profitability" in strengths or "profitability" in strengths
        assert "25" in strengths  # Should mention 25% EBITDA margin

    def test_rich_strengths_includes_funding(self, rich_company):
        """Rich data should include funding information."""
        strengths = AdaptiveTemplates.get_strengths_section(rich_company)

        assert "Investor" in strengths or "investor" in strengths.lower()
        assert "150" in strengths  # Should mention €150M funding

    def test_rich_strengths_includes_customers(self, rich_company):
        """Rich data should include customer information."""
        strengths = AdaptiveTemplates.get_strengths_section(rich_company)

        assert "Customer" in strengths or "customer" in strengths.lower()
        assert "Shell" in strengths or "BP" in strengths  # Should mention key customers

    def test_rich_strengths_includes_team(self, rich_company):
        """Rich data should include team size."""
        strengths = AdaptiveTemplates.get_strengths_section(rich_company)

        assert "Team" in strengths or "team" in strengths.lower()
        assert "500" in strengths  # Should mention 500 employees

    def test_data_quality_note_sparse(self, sparse_company):
        """Data quality note should reflect sparse data."""
        note = AdaptiveTemplates.get_data_quality_note(sparse_company)

        assert "Limited" in note
        assert "%" in note  # Should show percentage
        assert "recommended" in note.lower()

    def test_data_quality_note_moderate(self, moderate_company):
        """Data quality note should reflect moderate data."""
        note = AdaptiveTemplates.get_data_quality_note(moderate_company)

        assert "Moderate" in note
        assert "%" in note  # Should show percentage

    def test_data_quality_note_rich(self, rich_company):
        """Data quality note should reflect rich data."""
        note = AdaptiveTemplates.get_data_quality_note(rich_company)

        assert "Comprehensive" in note
        assert "%" in note  # Should show percentage

    def test_classification_narrative_phoenix(self, rich_company):
        """Phoenix classification should have growth-focused narrative."""
        narrative = AdaptiveTemplates.get_classification_narrative(rich_company)

        assert "high-growth" in narrative.lower()
        assert "Rich Data Company" in narrative
        assert "7.5" in narrative
        assert "Phoenix" not in narrative  # Should not repeat classification name

    def test_classification_narrative_salt(self, moderate_company):
        """Salt classification should have stability-focused narrative."""
        narrative = AdaptiveTemplates.get_classification_narrative(moderate_company)

        assert "stable" in narrative.lower() or "mature" in narrative.lower()
        assert "Moderate Data Company" in narrative
        assert "6.5" in narrative

    def test_classification_narrative_lead(self):
        """Lead classification should have transformation-focused narrative."""
        lead_company = Company(
            id="lead-1",
            name="Lead Company",
            industry="Energy Software",
            headquarters="Paris",
            description="Test lead company",
            composite_score=3.5,
            classification="Lead",
        )

        narrative = AdaptiveTemplates.get_classification_narrative(lead_company)

        assert "legacy" in narrative.lower()
        assert "transformation" in narrative.lower() or "modernization" in narrative.lower()
        assert "Lead Company" in narrative
        assert "3.5" in narrative

    def test_no_generic_filler_with_data(self, rich_company):
        """Should not use generic filler when specific data exists."""
        strengths = AdaptiveTemplates.get_strengths_section(rich_company)

        # Should NOT contain generic phrases
        assert "Market Position" not in strengths or "Established presence" not in strengths
        # Should contain specific metrics instead
        assert "60" in strengths or "250" in strengths or "500" in strengths

    def test_all_companies_have_strengths(self, sparse_company, moderate_company, rich_company):
        """All companies should have strengths section, regardless of data."""
        for company in [sparse_company, moderate_company, rich_company]:
            strengths = AdaptiveTemplates.get_strengths_section(company)

            assert "## Identified Strengths" in strengths
            assert len(strengths) > 50
            assert "No significant strengths" not in strengths.lower()

    def test_phoenix_narrative_differs_from_salt(self, rich_company, moderate_company):
        """Phoenix and Salt narratives should differ appropriately."""
        phoenix_narrative = AdaptiveTemplates.get_classification_narrative(rich_company)
        salt_narrative = AdaptiveTemplates.get_classification_narrative(moderate_company)

        assert phoenix_narrative != salt_narrative
        assert "high-growth" in phoenix_narrative.lower()
        assert "stable" in salt_narrative.lower() or "mature" in salt_narrative.lower()

    def test_completeness_threshold_sparse(self):
        """Test sparse threshold (< 40%)."""
        assert AdaptiveTemplates.SPARSE_THRESHOLD == 40

    def test_completeness_threshold_moderate(self):
        """Test moderate threshold (40-70%)."""
        assert AdaptiveTemplates.MODERATE_THRESHOLD == 70

    def test_completeness_threshold_rich(self):
        """Test rich threshold (> 70%)."""
        assert AdaptiveTemplates.RICH_THRESHOLD == 70
