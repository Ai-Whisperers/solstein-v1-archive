"""Tests for CompetitivePositionScorer."""

import pytest
from solstein.analytics.scorers.competitive_position import CompetitivePositionScorer
from solstein.domain.models import Company
from solstein.core.scoring_config import ScoringSettings


class TestCompetitivePositionScorer:
    """Test CompetitivePositionScorer comprehensively."""

    @pytest.fixture
    def scorer(self):
        return CompetitivePositionScorer()

    @pytest.fixture
    def baseline_company(self):
        return Company(
            id="test-1",
            name="Test Co",
            industry="SaaS",
            tier="Tier 2",
            ai_maturity="Strong",
            saas_maturity=8,
            geographic_presence=["US", "EU", "APAC"],
            tech_stack=["Python", "PostgreSQL", "Docker", "Kubernetes", "Redis"],
        )

    def test_score_returns_tuple(self, scorer, baseline_company):
        """Test that score returns (float, ScoringExplanation)."""
        result = scorer.score(baseline_company)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_score_within_bounds(self, scorer, baseline_company):
        """Test that score is between 0 and 10."""
        score, _ = scorer.score(baseline_company)
        assert 0.0 <= score <= 10.0

    def test_market_tier_scoring(self, scorer):
        """Test that market tier is scored."""
        company = Company(
            id="test-1",
            name="Test",
            industry="SaaS",
            tier="Tier 1",
        )
        score, expl = scorer.score(company)
        assert any(c.name == "Market Tier" for c in expl.components)

    def test_ai_maturity_scoring(self, scorer):
        """Test that AI maturity is scored."""
        company = Company(
            id="test-1",
            name="Test",
            industry="SaaS",
            ai_maturity="Very Strong",
        )
        score, expl = scorer.score(company)
        assert any(c.name == "AI Maturity" for c in expl.components)

    def test_saas_maturity_scoring(self, scorer):
        """Test that SaaS maturity is scored."""
        company = Company(
            id="test-1",
            name="Test",
            industry="SaaS",
            saas_maturity=9,
        )
        score, expl = scorer.score(company)
        assert any(c.name == "SaaS Maturity" for c in expl.components)

    def test_global_geographic_presence(self, scorer):
        """Test global geographic presence bonus."""
        company = Company(
            id="test-1",
            name="Test",
            industry="SaaS",
            geographic_presence=["US", "EU", "APAC", "LATAM", "MENA"],
        )
        score, expl = scorer.score(company)
        if (
            len(company.geographic_presence)
            > scorer.config.competitive.geo_global_count
        ):
            assert any(c.name == "Geographic Footprint" for c in expl.components)

    def test_regional_geographic_presence(self, scorer):
        """Test regional geographic presence bonus."""
        company = Company(
            id="test-1",
            name="Test",
            industry="SaaS",
            geographic_presence=["US", "EU"],
        )
        score, expl = scorer.score(company)
        if (
            len(company.geographic_presence)
            > scorer.config.competitive.geo_regional_count
        ):
            assert any(c.name == "Geographic Footprint" for c in expl.components)

    def test_tech_stack_diversity(self, scorer):
        """Test tech stack diversity bonus."""
        company = Company(
            id="test-1",
            name="Test",
            industry="SaaS",
            tech_stack=["Python", "Go", "Rust", "TypeScript", "Java", "Kotlin"],
        )
        score, expl = scorer.score(company)
        if len(company.tech_stack) > scorer.config.competitive.tech_diverse_count:
            assert any(c.name == "Stack Diversity" for c in expl.components)

    def test_limited_tech_stack(self, scorer):
        """Test with limited tech stack."""
        company = Company(
            id="test-1",
            name="Test",
            industry="SaaS",
            tech_stack=["Python"],
        )
        score, expl = scorer.score(company)
        assert 0.0 <= score <= 10.0

    def test_no_geographic_presence(self, scorer):
        """Test with no geographic presence."""
        company = Company(
            id="test-1",
            name="Test",
            industry="SaaS",
            geographic_presence=[],
        )
        score, expl = scorer.score(company)
        assert 0.0 <= score <= 10.0

    def test_explanation_populated(self, scorer, baseline_company):
        """Test that explanation is properly populated."""
        score, expl = scorer.score(baseline_company)
        assert expl.final_score == score
        assert len(expl.components) > 0
        for component in expl.components:
            assert component.name
            assert component.formula
            assert component.reasoning

    def test_custom_config(self):
        """Test with custom configuration."""
        config = ScoringSettings()
        config.competitive.base_score = 3.0
        scorer = CompetitivePositionScorer(config)
        company = Company(
            id="test-1",
            name="Test",
            industry="SaaS",
        )
        _, expl = scorer.score(company)
        assert expl.base_score == 3.0

    def test_consistency(self, scorer, baseline_company):
        """Test that scoring is deterministic."""
        score1, _ = scorer.score(baseline_company)
        score2, _ = scorer.score(baseline_company)
        assert score1 == score2

    def test_all_factors_combined(self, scorer, baseline_company):
        """Test with all factors present."""
        score, expl = scorer.score(baseline_company)
        components = [c.name for c in expl.components]
        assert "Market Tier" in components
        assert "AI Maturity" in components
        assert "SaaS Maturity" in components

    def test_saas_maturity_extremes(self, scorer):
        """Test SaaS maturity at extreme values."""
        for maturity in [1, 5, 10]:
            company = Company(
                id="test-1",
                name="Test",
                industry="SaaS",
                saas_maturity=maturity,
            )
            score, _ = scorer.score(company)
            assert 0.0 <= score <= 10.0

    def test_tier_2_vs_tier_1(self, scorer):
        """Test different tiers produce different scores."""
        tier1 = Company(
            id="test-1",
            name="T1",
            industry="SaaS",
            tier="Tier 1",
        )
        tier3 = Company(
            id="test-2",
            name="T3",
            industry="SaaS",
            tier="Tier 3",
        )
        score1, _ = scorer.score(tier1)
        score3, _ = scorer.score(tier3)
        assert (score1 - score3) != 0  # Different scores expected

    def test_ai_maturity_range(self, scorer):
        """Test all AI maturity levels."""
        maturities = ["None", "Low", "Moderate", "Strong", "Very Strong"]
        for maturity in maturities:
            company = Company(
                id="test-1",
                name="Test",
                industry="SaaS",
                ai_maturity=maturity,
            )
            score, _ = scorer.score(company)
            assert 0.0 <= score <= 10.0

    def test_geographic_thresholds(self, scorer):
        """Test various geographic presence levels."""
        for count in [1, 3, 5, 10]:
            company = Company(
                id="test-1",
                name="Test",
                industry="SaaS",
                geographic_presence=[f"Region{i}" for i in range(count)],
            )
            score, _ = scorer.score(company)
            assert 0.0 <= score <= 10.0

    def test_tech_stack_thresholds(self, scorer):
        """Test various tech stack sizes."""
        for count in [1, 3, 5, 10]:
            company = Company(
                id="test-1",
                name="Test",
                industry="SaaS",
                tech_stack=[f"Tech{i}" for i in range(count)],
            )
            score, _ = scorer.score(company)
            assert 0.0 <= score <= 10.0

    def test_component_values_numeric(self, scorer, baseline_company):
        """Test that all component values are numeric."""
        _, expl = scorer.score(baseline_company)
        for component in expl.components:
            assert isinstance(component.value, (int, float))

    def test_empty_company(self, scorer):
        """Test with minimal company data."""
        company = Company(
            id="test-1",
            name="Test",
            industry="SaaS",
        )
        score, _ = scorer.score(company)
        assert 0.0 <= score <= 10.0
