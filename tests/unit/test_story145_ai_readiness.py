"""Tests for STORY-145: AI Readiness Scoring Model (EPIC-038).

Validates:
- Four sub-dimensions scored correctly (data infra, tech debt, AI literacy, automation)
- Tier classification (AI-Ready, AI-Capable, AI-Challenged, AI-Resistant)
- Score range 0-100
- Integration with Company model fields
- Configurable weights
- Edge cases (empty company, missing fields)
"""

from __future__ import annotations

from solstein.analytics.ai_readiness import (
    AIReadinessConfig,
    AIReadinessResult,
    AIReadinessScorer,
    AIReadinessTier,
)
from solstein.domain.models import AIMaturity, Company, FinancialMetric

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_company(**overrides) -> Company:
    """Create a Company with sensible defaults for testing."""
    defaults: dict = {
        "id": "test-corp-001",
        "name": "Test Corp",
        "industry": "Technology",
    }
    defaults.update(overrides)
    return Company(**defaults)


def _make_ai_leader() -> Company:
    """Company with strong AI signals across all dimensions."""
    return _make_company(
        name="AI Leader Inc",
        ai_maturity=AIMaturity.VERY_STRONG,
        ai_score=9.0,
        ai_in_production=True,
        ai_key_capabilities="Advanced ML pipelines, NLP, computer vision deployed in production",
        ai_signal_level="Very High",
        saas_maturity=9,
        tech_stack=[
            "python",
            "kubernetes",
            "docker",
            "react",
            "typescript",
            "terraform",
            "aws",
            "kafka",
            "spark",
            "airflow",
        ],
        total_funding_raised_eur=200_000_000.0,
        data_availability="High",
        financials=FinancialMetric(
            revenue=500.0,
            growth_rate=35.0,
            employees=1000,
        ),
    )


def _make_ai_resistant() -> Company:
    """Company with no AI signals and legacy tech."""
    return _make_company(
        name="Legacy Corp",
        ai_maturity=AIMaturity.NONE,
        ai_score=0.0,
        ai_in_production=False,
        saas_maturity=1,
        tech_stack=["cobol", "mainframe"],
        total_funding_raised_eur=0.0,
        financials=FinancialMetric(
            revenue=10.0,
            growth_rate=-5.0,
            employees=50,
        ),
    )


# ---------------------------------------------------------------------------
# Basic scoring tests
# ---------------------------------------------------------------------------


class TestAIReadinessScorer:
    """Test the AIReadinessScorer produces correct results."""

    def test_score_returns_result_type(self):
        """Score returns an AIReadinessResult."""
        scorer = AIReadinessScorer()
        result = scorer.score(_make_company())
        assert isinstance(result, AIReadinessResult)

    def test_score_range_0_to_100(self):
        """Score is always within 0-100."""
        scorer = AIReadinessScorer()
        for company in [_make_company(), _make_ai_leader(), _make_ai_resistant()]:
            result = scorer.score(company)
            assert 0.0 <= result.score <= 100.0, f"Score {result.score} out of range"

    def test_four_dimensions_in_breakdown(self):
        """Breakdown contains exactly four dimensions."""
        scorer = AIReadinessScorer()
        result = scorer.score(_make_company())
        expected_keys = {"data_infrastructure", "technical_debt", "ai_literacy", "process_automation"}
        assert set(result.breakdown.keys()) == expected_keys

    def test_each_dimension_0_to_100(self):
        """Each dimension score is within 0-100."""
        scorer = AIReadinessScorer()
        result = scorer.score(_make_ai_leader())
        for dim, score in result.breakdown.items():
            assert 0.0 <= score <= 100.0, f"{dim} score {score} out of range"

    def test_insights_non_empty(self):
        """Insights list is never empty."""
        scorer = AIReadinessScorer()
        result = scorer.score(_make_company())
        assert len(result.insights) > 0


# ---------------------------------------------------------------------------
# Tier classification tests
# ---------------------------------------------------------------------------


class TestTierClassification:
    """Test tier classification boundaries."""

    def test_ai_leader_is_ready_or_capable(self):
        """Company with strong AI signals scores high."""
        scorer = AIReadinessScorer()
        result = scorer.score(_make_ai_leader())
        assert result.tier in (AIReadinessTier.AI_READY, AIReadinessTier.AI_CAPABLE)
        assert result.score >= 50.0

    def test_ai_resistant_scores_low(self):
        """Company with no AI signals and legacy tech scores low."""
        scorer = AIReadinessScorer()
        result = scorer.score(_make_ai_resistant())
        assert result.tier in (AIReadinessTier.AI_CHALLENGED, AIReadinessTier.AI_RESISTANT)
        assert result.score < 50.0

    def test_tier_boundaries(self):
        """Verify exact tier boundary classifications."""
        classify = AIReadinessScorer._classify
        assert classify(75.0) == AIReadinessTier.AI_READY
        assert classify(74.9) == AIReadinessTier.AI_CAPABLE
        assert classify(50.0) == AIReadinessTier.AI_CAPABLE
        assert classify(49.9) == AIReadinessTier.AI_CHALLENGED
        assert classify(25.0) == AIReadinessTier.AI_CHALLENGED
        assert classify(24.9) == AIReadinessTier.AI_RESISTANT
        assert classify(0.0) == AIReadinessTier.AI_RESISTANT

    def test_tier_enum_values(self):
        """Tier enum has the correct string values."""
        assert AIReadinessTier.AI_READY.value == "AI-Ready"
        assert AIReadinessTier.AI_CAPABLE.value == "AI-Capable"
        assert AIReadinessTier.AI_CHALLENGED.value == "AI-Challenged"
        assert AIReadinessTier.AI_RESISTANT.value == "AI-Resistant"


# ---------------------------------------------------------------------------
# Dimension-specific tests
# ---------------------------------------------------------------------------


class TestDataInfrastructureDimension:
    """Test the data infrastructure scoring dimension."""

    def test_high_saas_maturity_boosts_score(self):
        """High SaaS maturity increases data infrastructure score."""
        scorer = AIReadinessScorer()
        low_saas = scorer.score(_make_company(saas_maturity=1))
        high_saas = scorer.score(_make_company(saas_maturity=9))
        assert high_saas.breakdown["data_infrastructure"] > low_saas.breakdown["data_infrastructure"]

    def test_large_company_bonus(self):
        """Large employee count boosts data infrastructure score."""
        scorer = AIReadinessScorer()
        small = scorer.score(_make_company(financials=FinancialMetric(employees=10)))
        large = scorer.score(_make_company(financials=FinancialMetric(employees=600)))
        assert large.breakdown["data_infrastructure"] > small.breakdown["data_infrastructure"]


class TestTechnicalDebtDimension:
    """Test the technical debt scoring dimension."""

    def test_modern_stack_scores_higher(self):
        """Modern tech stack reduces technical debt score (= higher readiness)."""
        scorer = AIReadinessScorer()
        modern = scorer.score(_make_company(tech_stack=["python", "kubernetes", "docker", "react", "typescript"]))
        legacy = scorer.score(_make_company(tech_stack=["cobol", "mainframe"]))
        assert modern.breakdown["technical_debt"] > legacy.breakdown["technical_debt"]


class TestAILiteracyDimension:
    """Test the AI literacy scoring dimension."""

    def test_high_ai_maturity_scores_high(self):
        """High AI maturity enum boosts literacy score."""
        scorer = AIReadinessScorer()
        high = scorer.score(
            _make_company(
                ai_maturity=AIMaturity.VERY_STRONG,
                ai_score=9.0,
            )
        )
        low = scorer.score(
            _make_company(
                ai_maturity=AIMaturity.NONE,
                ai_score=0.0,
            )
        )
        assert high.breakdown["ai_literacy"] > low.breakdown["ai_literacy"]

    def test_production_ai_bonus(self):
        """Production AI deployment boosts literacy."""
        scorer = AIReadinessScorer()
        no_prod = scorer.score(_make_company(ai_in_production=False))
        prod = scorer.score(_make_company(ai_in_production=True))
        assert prod.breakdown["ai_literacy"] > no_prod.breakdown["ai_literacy"]


class TestProcessAutomationDimension:
    """Test the process automation scoring dimension."""

    def test_saas_maturity_boosts_automation(self):
        """High SaaS maturity increases automation score."""
        scorer = AIReadinessScorer()
        low = scorer.score(_make_company(saas_maturity=1))
        high = scorer.score(_make_company(saas_maturity=9))
        assert high.breakdown["process_automation"] > low.breakdown["process_automation"]


# ---------------------------------------------------------------------------
# Configuration tests
# ---------------------------------------------------------------------------


class TestAIReadinessConfig:
    """Test configurable weights and behavior."""

    def test_default_weights_sum_to_one(self):
        """Default weights sum to 1.0."""
        config = AIReadinessConfig()
        assert config.validate_weights()

    def test_custom_weights(self):
        """Custom weights change dimension influence."""
        # Heavy AI literacy weighting
        config = AIReadinessConfig(
            data_infrastructure_weight=0.10,
            technical_debt_weight=0.10,
            ai_literacy_weight=0.70,
            process_automation_weight=0.10,
        )
        scorer = AIReadinessScorer(config=config)
        result = scorer.score(
            _make_company(
                ai_maturity=AIMaturity.VERY_STRONG,
                ai_score=9.0,
                ai_in_production=True,
                ai_signal_level="Very High",
            )
        )
        # With heavy literacy weight, high AI maturity should push score up
        assert result.score > 50.0


# ---------------------------------------------------------------------------
# Company model integration tests
# ---------------------------------------------------------------------------


class TestCompanyModelIntegration:
    """Test that AI readiness fields work on Company model."""

    def test_company_has_ai_readiness_fields(self):
        """Company model has the new AI readiness fields."""
        c = Company(id="test-001", name="Test", industry="Tech")
        assert c.ai_readiness_score is None
        assert c.ai_readiness_tier is None
        assert c.ai_readiness_breakdown == {}

    def test_company_stores_ai_readiness(self):
        """AI readiness results can be stored on Company."""
        c = Company(id="test-001", name="Test", industry="Tech")
        scorer = AIReadinessScorer()
        result = scorer.score(c)
        c.ai_readiness_score = result.score
        c.ai_readiness_tier = result.tier.value
        c.ai_readiness_breakdown = result.breakdown
        assert c.ai_readiness_score == result.score
        assert c.ai_readiness_tier in ("AI-Ready", "AI-Capable", "AI-Challenged", "AI-Resistant")
        assert len(c.ai_readiness_breakdown) == 4


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Test edge cases and robustness."""

    def test_empty_company(self):
        """Scoring works on a company with minimal fields."""
        scorer = AIReadinessScorer()
        c = Company(id="empty-001", name="Empty", industry="Unknown")
        result = scorer.score(c)
        assert isinstance(result, AIReadinessResult)
        assert 0.0 <= result.score <= 100.0

    def test_none_financials(self):
        """Scoring handles None financials gracefully."""
        scorer = AIReadinessScorer()
        c = _make_company(financials=None)
        result = scorer.score(c)
        assert isinstance(result, AIReadinessResult)

    def test_all_none_ai_fields(self):
        """Scoring handles all None AI fields."""
        scorer = AIReadinessScorer()
        c = _make_company(
            ai_score=None,
            ai_in_production=None,
            ai_key_capabilities=None,
            ai_signal_level=None,
        )
        result = scorer.score(c)
        assert isinstance(result, AIReadinessResult)
        assert 0.0 <= result.score <= 100.0
