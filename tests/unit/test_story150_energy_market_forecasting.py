"""Tests for STORY-150: Energy Market Forecasting & Demand Scoring.

Validates the EnergyMarketScorer against known market-aligned vs.
misaligned energy company profiles.
"""

from __future__ import annotations

import pytest

from solstein.analytics.energy_market_forecasting import (
    DemandSegment,
    EnergyMarketResult,
    EnergyMarketScorer,
    MarketPositioning,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_company(**overrides):  # type: ignore[no-untyped-def]
    """Create a minimal Company for testing."""
    from solstein.domain.models import Company

    defaults = {
        "id": "market-test-001",
        "name": "MarketCorp",
        "industry": "Energy Software",
        "revenue": 10_000_000,
        "employees": 150,
    }
    defaults.update(overrides)
    return Company(**defaults)


@pytest.fixture
def scorer() -> EnergyMarketScorer:
    return EnergyMarketScorer()


# ---------------------------------------------------------------------------
# TestResultStructure
# ---------------------------------------------------------------------------

class TestResultStructure:
    """Verify the market result has all required fields."""

    def test_returns_result(self, scorer: EnergyMarketScorer) -> None:
        result = scorer.score(_make_company())
        assert isinstance(result, EnergyMarketResult)

    def test_has_three_dimension_scores(self, scorer: EnergyMarketScorer) -> None:
        result = scorer.score(_make_company())
        assert 0 <= result.market_alignment_score <= 100
        assert 0 <= result.demand_resilience_score <= 100
        assert 0 <= result.forecasting_capability_score <= 100

    def test_has_composite_score(self, scorer: EnergyMarketScorer) -> None:
        result = scorer.score(_make_company())
        assert 0 <= result.composite_score <= 100

    def test_has_market_positioning(self, scorer: EnergyMarketScorer) -> None:
        result = scorer.score(_make_company())
        assert result.market_positioning in (
            MarketPositioning.LEADER,
            MarketPositioning.ALIGNED,
            MarketPositioning.TRANSITIONING,
            MarketPositioning.MISALIGNED,
            MarketPositioning.UNKNOWN,
        )

    def test_has_breakdown(self, scorer: EnergyMarketScorer) -> None:
        result = scorer.score(_make_company())
        assert "alignment_weight" in result.breakdown
        assert "resilience_weight" in result.breakdown
        assert "segment_count" in result.breakdown


# ---------------------------------------------------------------------------
# TestSegmentDetection
# ---------------------------------------------------------------------------

class TestSegmentDetection:
    """Verify demand segment detection from company data."""

    def test_renewables_detected(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(description="Solar and wind energy platform")
        result = scorer.score(company)
        assert DemandSegment.RENEWABLES_INTEGRATION in result.primary_segments

    def test_grid_modernization_detected(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(description="Smart grid analytics and ADMS")
        result = scorer.score(company)
        assert DemandSegment.GRID_MODERNIZATION in result.primary_segments

    def test_ev_infrastructure_detected(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(description="EV charging station management")
        result = scorer.score(company)
        assert DemandSegment.EV_INFRASTRUCTURE in result.primary_segments

    def test_storage_detected(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(description="Battery energy storage system BESS")
        result = scorer.score(company)
        assert DemandSegment.ENERGY_STORAGE in result.primary_segments

    def test_multiple_segments_detected(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(
            description="Solar renewable integration with battery storage and EV charging"
        )
        result = scorer.score(company)
        assert len(result.primary_segments) >= 3

    def test_no_segments_for_generic(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(description="A generic software company")
        result = scorer.score(company)
        assert result.market_positioning == MarketPositioning.UNKNOWN


# ---------------------------------------------------------------------------
# TestMarketAlignment
# ---------------------------------------------------------------------------

class TestMarketAlignment:
    """Verify market alignment scoring."""

    def test_growth_segments_score_higher(self, scorer: EnergyMarketScorer) -> None:
        growth = _make_company(description="Battery energy storage and EV charging")
        decline = _make_company(description="Coal thermal plant natural gas generation")
        r_growth = scorer.score(growth)
        r_decline = scorer.score(decline)
        assert r_growth.market_alignment_score > r_decline.market_alignment_score

    def test_multiple_growth_segments_boost(self, scorer: EnergyMarketScorer) -> None:
        single = _make_company(description="Solar renewable energy")
        multi = _make_company(
            description="Solar renewable energy with battery storage and smart grid"
        )
        r_single = scorer.score(single)
        r_multi = scorer.score(multi)
        assert r_multi.market_alignment_score >= r_single.market_alignment_score

    def test_declining_segment_penalty(self, scorer: EnergyMarketScorer) -> None:
        clean = _make_company(description="Solar renewable energy platform")
        mixed = _make_company(
            description="Solar renewable and coal fossil fuel generation"
        )
        r_clean = scorer.score(clean)
        r_mixed = scorer.score(mixed)
        assert r_clean.market_alignment_score > r_mixed.market_alignment_score


# ---------------------------------------------------------------------------
# TestDemandResilience
# ---------------------------------------------------------------------------

class TestDemandResilience:
    """Verify demand resilience scoring."""

    def test_diversified_scores_higher(self, scorer: EnergyMarketScorer) -> None:
        narrow = _make_company(description="Solar energy only")
        broad = _make_company(
            description="Solar renewable with battery storage and demand response"
        )
        r_narrow = scorer.score(narrow)
        r_broad = scorer.score(broad)
        assert r_broad.demand_resilience_score > r_narrow.demand_resilience_score

    def test_high_growth_boosts_resilience(self, scorer: EnergyMarketScorer) -> None:
        low_growth = _make_company(description="Solar energy", growth_rate=-5.0)
        high_growth = _make_company(description="Solar energy", growth_rate=20.0)
        r_low = scorer.score(low_growth)
        r_high = scorer.score(high_growth)
        assert r_high.demand_resilience_score > r_low.demand_resilience_score

    def test_saas_maturity_boosts_resilience(self, scorer: EnergyMarketScorer) -> None:
        low_saas = _make_company(description="Solar energy", saas_maturity=1)
        high_saas = _make_company(description="Solar energy", saas_maturity=8)
        r_low = scorer.score(low_saas)
        r_high = scorer.score(high_saas)
        assert r_high.demand_resilience_score > r_low.demand_resilience_score


# ---------------------------------------------------------------------------
# TestForecastingCapability
# ---------------------------------------------------------------------------

class TestForecastingCapability:
    """Verify forecasting capability scoring."""

    def test_analytics_keywords_boost(self, scorer: EnergyMarketScorer) -> None:
        basic = _make_company(description="Energy company")
        advanced = _make_company(
            description="Machine learning predictive analytics with demand forecasting"
        )
        r_basic = scorer.score(basic)
        r_advanced = scorer.score(advanced)
        assert r_advanced.forecasting_capability_score > r_basic.forecasting_capability_score

    def test_ai_maturity_boosts_forecasting(self, scorer: EnergyMarketScorer) -> None:
        low_ai = _make_company(description="Energy company", ai_maturity="None")
        high_ai = _make_company(description="Energy company", ai_maturity="Strong")
        r_low = scorer.score(low_ai)
        r_high = scorer.score(high_ai)
        assert r_high.forecasting_capability_score > r_low.forecasting_capability_score

    def test_analytics_tech_stack_boost(self, scorer: EnergyMarketScorer) -> None:
        basic = _make_company(tech_stack=["java"])
        analytics = _make_company(tech_stack=["python", "tensorflow", "spark"])
        r_basic = scorer.score(basic)
        r_analytics = scorer.score(analytics)
        assert r_analytics.forecasting_capability_score > r_basic.forecasting_capability_score


# ---------------------------------------------------------------------------
# TestMarketPositioning
# ---------------------------------------------------------------------------

class TestMarketPositioning:
    """Verify market positioning classification."""

    def test_leader_positioning(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(
            description=(
                "Solar renewable with battery energy storage, "
                "EV charging, smart grid, machine learning predictive "
                "analytics demand forecasting, diversified multi-market"
            ),
            ai_maturity="Strong",
            saas_maturity=8,
            growth_rate=25.0,
            tech_stack=["python", "tensorflow"],
        )
        result = scorer.score(company)
        assert result.market_positioning == MarketPositioning.LEADER

    def test_misaligned_positioning(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(
            description="Coal fossil fuel thermal plant combined cycle",
            saas_maturity=1,
            ai_maturity="None",
        )
        result = scorer.score(company)
        assert result.market_positioning == MarketPositioning.MISALIGNED


# ---------------------------------------------------------------------------
# TestRecommendations
# ---------------------------------------------------------------------------

class TestRecommendations:
    """Verify recommendations generation."""

    def test_misaligned_has_recommendations(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(
            description="Coal thermal plant",
            saas_maturity=1,
            ai_maturity="None",
        )
        result = scorer.score(company)
        assert len(result.recommendations) > 0

    def test_leader_has_no_risk_recommendations(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(
            description=(
                "Solar renewable battery energy storage EV charging "
                "smart grid machine learning predictive analytics "
                "demand forecasting diversified multi-market"
            ),
            ai_maturity="Strong",
            saas_maturity=8,
            growth_rate=25.0,
            tech_stack=["python", "tensorflow"],
        )
        result = scorer.score(company)
        # Leader should have no risk-driven recommendations
        assert len(result.risk_factors) == 0

    def test_unknown_has_clarification_rec(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(description="A generic software company")
        result = scorer.score(company)
        recs_text = " ".join(result.recommendations).lower()
        assert "clarify" in recs_text or "identify" in recs_text or "position" in recs_text


# ---------------------------------------------------------------------------
# TestCompanyModelIntegration
# ---------------------------------------------------------------------------

class TestCompanyModelIntegration:
    """Verify Company model has market forecasting fields."""

    def test_company_has_market_fields(self) -> None:
        company = _make_company()
        assert hasattr(company, "energy_market_score")
        assert hasattr(company, "energy_market_positioning")
        assert hasattr(company, "energy_market_segments")
        assert hasattr(company, "energy_market_breakdown")

    def test_store_market_results(self, scorer: EnergyMarketScorer) -> None:
        company = _make_company(description="Solar renewable energy")
        result = scorer.score(company)
        company.energy_market_score = result.composite_score
        company.energy_market_positioning = result.market_positioning.value
        assert company.energy_market_score is not None
        assert company.energy_market_positioning in (
            "leader", "aligned", "transitioning", "misaligned", "unknown",
        )
