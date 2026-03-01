"""Unit tests for Financial Health Scoring - EPIC-001 Story 1.5.

Tests verify that unit conversions are handled correctly:
- Revenue stored in millions (e.g., 5.0 = €5M) but calculations use actual EUR
- Efficiency calculated as (revenue * 1,000,000) / employees
- Funding cushion ratio uses both values in millions (unitless ratio)
"""

import pytest

from solstein.analytics.scorers.financial_health import FinancialHealthScorer
from solstein.core.scoring_config import FinancialHealthConfig, ScoringSettings
from solstein.domain.models import FinancialMetric


class TestFinancialHealthUnitConversions:
    """Test that unit conversions are handled correctly in financial health scoring."""

    @pytest.fixture
    def scorer(self):
        """Create a FinancialHealthScorer with default config."""
        return FinancialHealthScorer()

    @pytest.fixture
    def config(self):
        """Create a ScoringSettings config for reference."""
        return ScoringSettings()

    def test_revenue_scale_thresholds_in_millions(self, scorer, config):
        """Test that revenue scale thresholds work with values in millions.
        
        Revenue is stored as 5.0 (meaning €5M), not 5_000_000.
        Thresholds are configured in millions.
        """
        cfg = config.financial
        
        # Small revenue: < €1M (stored as < 1.0)
        small = FinancialMetric(revenue=0.5)  # €500K
        score_small, expl_small = scorer.score(small)
        assert any(c.name == "Revenue Scale" for c in expl_small.components)
        
        # Medium revenue: €1M - €100M (stored as 1.0 - 100.0)
        medium = FinancialMetric(revenue=10.0)  # €10M
        score_medium, expl_medium = scorer.score(medium)
        assert any(c.name == "Revenue Scale" for c in expl_medium.components)
        
        # Large revenue: > €100M (stored as > 100.0)
        large = FinancialMetric(revenue=150.0)  # €150M
        score_large, expl_large = scorer.score(large)
        assert any(c.name == "Revenue Scale" for c in expl_large.components)
        
        # Verify ordering: large > medium > small
        assert score_large > score_medium > score_small

    def test_efficiency_calculation_with_unit_conversion(self, scorer, config):
        """Test that efficiency correctly converts revenue from millions to EUR.
        
        Revenue per employee = (revenue_millions * 1_000_000) / employees
        Example: €5M revenue, 50 employees = (5.0 * 1_000_000) / 50 = €100K per employee
        """
        cfg = config.financial
        
        # Exceptional efficiency: > €1M per employee
        # Need: (revenue * 1M) / employees > 1M
        # So: revenue > employees
        exceptional = FinancialMetric(
            revenue=60.0,  # €60M
            employees=50,  # 60M / 50 = €1.2M per employee
        )
        score_exc, expl_exc = scorer.score(exceptional)
        
        # Should get efficiency bonus
        efficiency_components = [c for c in expl_exc.components if c.name == "Operating Efficiency"]
        assert len(efficiency_components) > 0
        assert efficiency_components[0].value > 0  # Positive bonus
        
        # Low efficiency: < €100K per employee
        low = FinancialMetric(
            revenue=5.0,  # €5M
            employees=100,  # 5M / 100 = €50K per employee
        )
        score_low, expl_low = scorer.score(low)
        
        efficiency_components_low = [c for c in expl_low.components if c.name == "Operating Efficiency"]
        assert len(efficiency_components_low) > 0
        assert efficiency_components_low[0].value < 0  # Negative penalty

    def test_efficiency_formula_calculation(self, scorer):
        """Test the exact efficiency formula calculation."""
        # €10M revenue, 100 employees = €100K per employee (at threshold)
        financials = FinancialMetric(
            revenue=10.0,
            employees=100,
        )
        
        score, expl = scorer.score(financials)
        
        # Calculate expected revenue per employee
        expected_rev_per_emp = (10.0 * 1_000_000) / 100  # €100,000
        
        # Find efficiency component
        efficiency_comp = next((c for c in expl.components if c.name == "Operating Efficiency"), None)
        
        if efficiency_comp:
            # Verify the formula shows correct calculation
            assert "rev_per_emp" in efficiency_comp.formula
            # The formula should show €100,000 (or close to it)
            assert "100000" in efficiency_comp.formula or "100,000" in efficiency_comp.formula

    def test_funding_cushion_ratio_unitless(self, scorer):
        """Test that funding cushion ratio is unitless (both in millions).
        
        Ratio = funding_raised_millions / revenue_millions
        Example: €10M funding / €5M revenue = 2.0 ratio
        """
        # High cushion: > 10x ratio
        high_cushion = FinancialMetric(
            revenue=5.0,  # €5M
            funding_raised=100.0,  # €100M (20x ratio)
            profit_margin=10.0,  # Profitable
        )
        score_high, expl_high = scorer.score(high_cushion)
        
        cushion_components = [c for c in expl_high.components if c.name == "Funding Cushion"]
        assert len(cushion_components) > 0
        assert cushion_components[0].value > 0  # Positive bonus
        
        # Thin cushion with unprofitable: < 0.5x ratio
        thin_cushion = FinancialMetric(
            revenue=10.0,  # €10M
            funding_raised=3.0,  # €3M (0.3x ratio)
            profit_margin=-5.0,  # Unprofitable
        )
        score_thin, expl_thin = scorer.score(thin_cushion)
        
        cushion_components_thin = [c for c in expl_thin.components if c.name == "Funding Cushion"]
        assert len(cushion_components_thin) > 0
        assert cushion_components_thin[0].value < 0  # Negative penalty

    def test_funding_cushion_formula_shows_correct_ratio(self, scorer):
        """Test that funding cushion formula shows the correct ratio calculation."""
        financials = FinancialMetric(
            revenue=5.0,  # €5M
            funding_raised=15.0,  # €15M
            profit_margin=10.0,
        )
        
        score, expl = scorer.score(financials)
        
        cushion_comp = next((c for c in expl.components if c.name == "Funding Cushion"), None)
        
        if cushion_comp:
            # Ratio should be 3.0 (15.0 / 5.0)
            assert "3.0" in cushion_comp.formula or "3.00" in cushion_comp.formula
            assert "funding_ratio" in cushion_comp.formula

    def test_real_world_company_example(self, scorer):
        """Test with a realistic company profile.
        
        Example: Mid-size SaaS company
        - Revenue: €25M (stored as 25.0)
        - Profit margin: 15%
        - Employees: 40 (to get efficiency bonus: €625K per employee > €500K threshold)
        - Funding: €100M (to get cushion bonus: 4x ratio > 3x threshold)
        """
        company = FinancialMetric(
            revenue=25.0,  # €25M
            profit_margin=15.0,  # 15%
            employees=40,  # 40 people = €625K per employee (> €500K threshold for bonus)
            funding_raised=100.0,  # €100M = 4x ratio (> 3x threshold for bonus)
        )
        
        score, expl = scorer.score(company)
        
        # Should have multiple components
        component_names = [c.name for c in expl.components]
        assert "Revenue Scale" in component_names
        assert "Profitability Health" in component_names
        assert "Operating Efficiency" in component_names
        assert "Funding Cushion" in component_names
        
        # Verify efficiency calculation: (25M * 1M) / 40 = €625K per employee
        efficiency_comp = next(c for c in expl.components if c.name == "Operating Efficiency")
        assert "625000" in efficiency_comp.formula or "625,000" in efficiency_comp.formula
        
        # Verify cushion ratio: 100M / 25M = 4.0
        cushion_comp = next(c for c in expl.components if c.name == "Funding Cushion")
        assert "4.0" in cushion_comp.formula or "4.00" in cushion_comp.formula
        
        # Score should be reasonable for a healthy company
        assert 5.0 <= score <= 10.0

    def test_edge_case_very_small_company(self, scorer):
        """Test with a very small startup."""
        startup = FinancialMetric(
            revenue=0.1,  # €100K
            profit_margin=-20.0,  # Burning cash
            employees=5,
            funding_raised=1.0,  # €1M
        )
        
        score, expl = scorer.score(startup)
        
        # Should handle gracefully
        assert 0.0 <= score <= 10.0
        
        # Should have revenue scale penalty
        revenue_comp = next((c for c in expl.components if c.name == "Revenue Scale"), None)
        if revenue_comp:
            assert revenue_comp.value < 0

    def test_edge_case_enterprise_company(self, scorer):
        """Test with a large enterprise company."""
        enterprise = FinancialMetric(
            revenue=500.0,  # €500M
            profit_margin=25.0,  # Very profitable
            employees=5000,
            funding_raised=1000.0,  # €1B (maybe public)
        )
        
        score, expl = scorer.score(enterprise)
        
        # Should have high score
        assert score >= 7.0
        
        # Should have all positive components
        for comp in expl.components:
            assert comp.value > 0

    def test_config_thresholds_are_in_millions(self):
        """Verify that config thresholds are correctly set in millions."""
        config = FinancialHealthConfig()
        
        # Revenue thresholds should be in millions
        assert config.revenue_large_threshold == 100.0  # €100M
        assert config.revenue_med_threshold == 10.0  # €10M
        assert config.revenue_small_threshold == 1.0  # €1M
        
        # Efficiency thresholds should be in actual EUR per employee
        assert config.efficiency_exceptional_threshold == 1_000_000.0  # €1M
        assert config.efficiency_good_threshold == 500_000.0  # €500K
        assert config.efficiency_low_threshold == 100_000.0  # €100K
        
        # Funding cushion ratios are unitless
        assert config.cushion_high_ratio == 10.0  # 10x
        assert config.cushion_med_ratio == 3.0  # 3x
        assert config.cushion_thin_ratio == 0.5  # 0.5x

    def test_revenue_none_does_not_crash(self, scorer):
        """Test that None revenue doesn't cause errors."""
        financials = FinancialMetric(
            revenue=None,
            profit_margin=10.0,
            employees=100,
        )
        
        score, expl = scorer.score(financials)
        
        # Should still work
        assert 0.0 <= score <= 10.0
        
        # Should not have revenue scale component
        assert not any(c.name == "Revenue Scale" for c in expl.components)

    def test_employees_none_does_not_crash(self, scorer):
        """Test that None employees doesn't cause errors."""
        financials = FinancialMetric(
            revenue=10.0,
            profit_margin=10.0,
            employees=None,
        )
        
        score, expl = scorer.score(financials)
        
        # Should still work
        assert 0.0 <= score <= 10.0
        
        # Should not have efficiency component
        assert not any(c.name == "Operating Efficiency" for c in expl.components)

    def test_zero_employees_does_not_divide_by_zero(self, scorer):
        """Test that zero employees doesn't cause division by zero."""
        financials = FinancialMetric(
            revenue=10.0,
            employees=0,
        )
        
        score, expl = scorer.score(financials)
        
        # Should not crash
        assert 0.0 <= score <= 10.0
        
        # Should not have efficiency component (division by zero avoided)
        assert not any(c.name == "Operating Efficiency" for c in expl.components)


class TestFinancialHealthConfigValidation:
    """Test that scoring configuration values are valid."""

    def test_default_config_values(self):
        """Test that default config values are reasonable."""
        config = ScoringSettings()
        financial = config.financial
        
        # Base score should be middle range
        assert 0.0 <= financial.base_score <= 10.0
        
        # Revenue thresholds should be ordered correctly
        assert financial.revenue_small_threshold < financial.revenue_med_threshold < financial.revenue_large_threshold
        
        # Efficiency thresholds should be ordered
        assert financial.efficiency_low_threshold < financial.efficiency_good_threshold < financial.efficiency_exceptional_threshold
        
        # Funding cushion ratios should be ordered
        assert financial.cushion_thin_ratio < financial.cushion_med_ratio < financial.cushion_high_ratio
        
        # Profitability thresholds should be ordered
        assert financial.margin_med_threshold < financial.margin_high_threshold

    def test_config_bounds(self):
        """Test that config values are within reasonable bounds."""
        config = FinancialHealthConfig()
        
        # All thresholds should be positive
        assert config.revenue_large_threshold > 0
        assert config.efficiency_exceptional_threshold > 0
        assert config.cushion_high_ratio > 0
        
        # Bonuses should be reasonable (not too large)
        assert config.revenue_large_bonus <= 5.0
        assert config.efficiency_exceptional_bonus <= 5.0

    def test_custom_config_override(self):
        """Test that custom config values can be set."""
        config = ScoringSettings()
        config.financial.revenue_large_threshold = 200.0  # €200M
        config.financial.efficiency_exceptional_threshold = 2_000_000.0  # €2M per employee
        
        scorer = FinancialHealthScorer(config)
        
        # Test with custom thresholds
        financials = FinancialMetric(
            revenue=150.0,  # €150M - now medium, not large
            employees=100,
        )
        
        score, expl = scorer.score(financials)
        
        # Should still work with custom thresholds
        assert 0.0 <= score <= 10.0


class TestFinancialHealthExplanation:
    """Test that scoring explanations are comprehensive and accurate."""

    def test_explanation_includes_all_applicable_components(self, scorer):
        """Test that explanation includes all applicable scoring components."""
        financials = FinancialMetric(
            revenue=50.0,  # €50M
            profit_margin=20.0,  # High margin
            employees=50,  # €1M per employee (exceptional)
            funding_raised=200.0,  # €200M (4x ratio)
        )
        
        score, expl = scorer.score(financials)
        
        # Should have all 4 components
        component_names = {c.name for c in expl.components}
        expected = {"Revenue Scale", "Profitability Health", "Operating Efficiency", "Funding Cushion"}
        assert component_names == expected

    def test_explanation_formulas_are_informative(self, scorer):
        """Test that explanation formulas are informative."""
        financials = FinancialMetric(
            revenue=25.0,
            profit_margin=15.0,
            employees=40,
            funding_raised=100.0,
        )
        
        score, expl = scorer.score(financials)
        
        for comp in expl.components:
            # Each component should have a formula
            assert comp.formula
            assert len(comp.formula) > 0
            
            # Each component should have reasoning
            assert comp.reasoning
            assert len(comp.reasoning) > 0
            
            # Formula should include relevant values
            if comp.name == "Revenue Scale":
                assert "revenue" in comp.formula.lower()
            elif comp.name == "Profitability Health":
                assert "margin" in comp.formula.lower()
            elif comp.name == "Operating Efficiency":
                assert "rev_per_emp" in comp.formula
            elif comp.name == "Funding Cushion":
                assert "funding_ratio" in comp.formula

    def test_final_score_matches_sum(self, scorer):
        """Test that final score is base + sum of components (within bounds)."""
        financials = FinancialMetric(
            revenue=50.0,
            profit_margin=20.0,
            employees=50,
            funding_raised=200.0,
        )
        
        score, expl = scorer.score(financials)
        
        # Calculate expected score
        expected = expl.base_score + sum(c.value for c in expl.components)
        
        # Should match (within floating point tolerance)
        assert abs(score - expected) < 0.01
        
        # Should be clamped to [0, 10]
        assert 0.0 <= score <= 10.0
        assert expl.final_score == score
