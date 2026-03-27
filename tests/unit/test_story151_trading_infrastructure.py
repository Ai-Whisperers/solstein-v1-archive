"""Tests for STORY-151: Trading Platform & Digital Infrastructure Assessment.

Validates the TradingInfrastructureScorer against known advanced vs.
basic energy company infrastructure profiles.
"""

from __future__ import annotations

import pytest

from solstein.analytics.energy_trading_infrastructure import (
    InfrastructureTier,
    PlatformMaturity,
    TradingInfrastructureResult,
    TradingInfrastructureScorer,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_company(**overrides):  # type: ignore[no-untyped-def]
    """Create a minimal Company for testing."""
    from solstein.domain.models import Company

    defaults = {
        "id": "infra-test-001",
        "name": "InfraCorp",
        "industry": "Energy Software",
        "revenue": 10_000_000,
        "employees": 150,
    }
    defaults.update(overrides)
    return Company(**defaults)


@pytest.fixture
def scorer() -> TradingInfrastructureScorer:
    return TradingInfrastructureScorer()


# ---------------------------------------------------------------------------
# TestResultStructure
# ---------------------------------------------------------------------------

class TestResultStructure:
    """Verify the infrastructure result has all required fields."""

    def test_returns_result(self, scorer: TradingInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert isinstance(result, TradingInfrastructureResult)

    def test_has_three_dimension_scores(self, scorer: TradingInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert 0 <= result.trading_platform_score <= 100
        assert 0 <= result.digital_infrastructure_score <= 100
        assert 0 <= result.integration_readiness_score <= 100

    def test_has_composite_score(self, scorer: TradingInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert 0 <= result.composite_score <= 100

    def test_has_platform_maturity(self, scorer: TradingInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert isinstance(result.platform_maturity, PlatformMaturity)

    def test_has_infrastructure_tier(self, scorer: TradingInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert isinstance(result.infrastructure_tier, InfrastructureTier)

    def test_has_breakdown(self, scorer: TradingInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert "trading_weight" in result.breakdown
        assert "infrastructure_weight" in result.breakdown


# ---------------------------------------------------------------------------
# TestTradingPlatform
# ---------------------------------------------------------------------------

class TestTradingPlatform:
    """Verify trading platform scoring."""

    def test_algo_trading_boosts_score(self, scorer: TradingInfrastructureScorer) -> None:
        basic = _make_company(description="Basic energy company")
        algo = _make_company(
            description="Algorithmic trading with energy trading platform"
        )
        r_basic = scorer.score(basic)
        r_algo = scorer.score(algo)
        assert r_algo.trading_platform_score > r_basic.trading_platform_score

    def test_market_access_boosts_score(self, scorer: TradingInfrastructureScorer) -> None:
        basic = _make_company(description="Basic energy")
        market = _make_company(
            description="Day-ahead intraday futures market access with epex"
        )
        r_basic = scorer.score(basic)
        r_market = scorer.score(market)
        assert r_market.trading_platform_score > r_basic.trading_platform_score

    def test_risk_management_boosts_score(self, scorer: TradingInfrastructureScorer) -> None:
        basic = _make_company(description="Basic energy")
        risk = _make_company(
            description="Value at risk position management with counterparty risk"
        )
        r_basic = scorer.score(basic)
        r_risk = scorer.score(risk)
        assert r_risk.trading_platform_score > r_basic.trading_platform_score

    def test_advanced_maturity_full_stack(self, scorer: TradingInfrastructureScorer) -> None:
        company = _make_company(
            description=(
                "Algorithmic trading energy trading platform with "
                "day-ahead intraday futures and value at risk "
                "position management counterparty risk"
            )
        )
        result = scorer.score(company)
        assert result.platform_maturity == PlatformMaturity.ADVANCED


# ---------------------------------------------------------------------------
# TestDigitalInfrastructure
# ---------------------------------------------------------------------------

class TestDigitalInfrastructure:
    """Verify digital infrastructure scoring."""

    def test_cloud_boosts_score(self, scorer: TradingInfrastructureScorer) -> None:
        basic = _make_company(tech_stack=["java"])
        cloud = _make_company(tech_stack=["aws", "kubernetes", "docker"])
        r_basic = scorer.score(basic)
        r_cloud = scorer.score(cloud)
        assert r_cloud.digital_infrastructure_score > r_basic.digital_infrastructure_score

    def test_api_maturity_boosts_score(self, scorer: TradingInfrastructureScorer) -> None:
        basic = _make_company(description="Basic company")
        api = _make_company(
            description="REST api with graphql microservices and event-driven architecture"
        )
        r_basic = scorer.score(basic)
        r_api = scorer.score(api)
        assert r_api.digital_infrastructure_score > r_basic.digital_infrastructure_score

    def test_data_architecture_boosts_score(self, scorer: TradingInfrastructureScorer) -> None:
        basic = _make_company(description="Basic company")
        data = _make_company(
            description="Data lake with streaming kafka and time series database"
        )
        r_basic = scorer.score(basic)
        r_data = scorer.score(data)
        assert r_data.digital_infrastructure_score > r_basic.digital_infrastructure_score

    def test_saas_maturity_boosts_score(self, scorer: TradingInfrastructureScorer) -> None:
        low = _make_company(saas_maturity=1)
        high = _make_company(saas_maturity=8)
        r_low = scorer.score(low)
        r_high = scorer.score(high)
        assert r_high.digital_infrastructure_score > r_low.digital_infrastructure_score

    def test_cloud_native_tier(self, scorer: TradingInfrastructureScorer) -> None:
        company = _make_company(
            tech_stack=["aws", "kubernetes", "docker", "kafka"],
            description=(
                "Cloud-native api microservices with data lake "
                "streaming and graphql event-driven"
            ),
            saas_maturity=9,
        )
        result = scorer.score(company)
        assert result.infrastructure_tier == InfrastructureTier.CLOUD_NATIVE


# ---------------------------------------------------------------------------
# TestIntegrationReadiness
# ---------------------------------------------------------------------------

class TestIntegrationReadiness:
    """Verify integration readiness scoring."""

    def test_standards_boost_score(self, scorer: TradingInfrastructureScorer) -> None:
        basic = _make_company(description="Basic company")
        standards = _make_company(
            description="IEC 61968 CIM interoperability with openapi and edi"
        )
        r_basic = scorer.score(basic)
        r_std = scorer.score(standards)
        assert r_std.integration_readiness_score > r_basic.integration_readiness_score

    def test_security_boosts_score(self, scorer: TradingInfrastructureScorer) -> None:
        basic = _make_company(description="Basic company")
        secure = _make_company(
            description="Zero trust SSO OAuth with encryption and SIEM"
        )
        r_basic = scorer.score(basic)
        r_secure = scorer.score(secure)
        assert r_secure.integration_readiness_score > r_basic.integration_readiness_score


# ---------------------------------------------------------------------------
# TestRecommendations
# ---------------------------------------------------------------------------

class TestRecommendations:
    """Verify recommendations generation."""

    def test_basic_has_recommendations(self, scorer: TradingInfrastructureScorer) -> None:
        company = _make_company(description="A basic energy company", saas_maturity=1)
        result = scorer.score(company)
        assert len(result.recommendations) > 0

    def test_advanced_has_fewer_gaps(self, scorer: TradingInfrastructureScorer) -> None:
        basic = _make_company(description="Basic company", saas_maturity=1)
        advanced = _make_company(
            tech_stack=["aws", "kubernetes", "docker", "kafka"],
            description=(
                "Algorithmic trading energy trading platform with "
                "cloud-native api microservices data lake streaming "
                "IEC 61968 CIM interoperability openapi zero trust SSO OAuth "
                "day-ahead intraday value at risk position management"
            ),
            saas_maturity=9,
        )
        r_basic = scorer.score(basic)
        r_advanced = scorer.score(advanced)
        assert len(r_advanced.gaps) < len(r_basic.gaps)


# ---------------------------------------------------------------------------
# TestCompanyModelIntegration
# ---------------------------------------------------------------------------

class TestCompanyModelIntegration:
    """Verify Company model has trading infrastructure fields."""

    def test_company_has_trading_fields(self) -> None:
        company = _make_company()
        assert hasattr(company, "energy_trading_score")
        assert hasattr(company, "energy_platform_maturity")
        assert hasattr(company, "energy_infrastructure_tier")
        assert hasattr(company, "energy_trading_breakdown")

    def test_store_trading_results(self, scorer: TradingInfrastructureScorer) -> None:
        company = _make_company(
            description="Algorithmic trading energy trading platform"
        )
        result = scorer.score(company)
        company.energy_trading_score = result.composite_score
        company.energy_platform_maturity = result.platform_maturity.value
        company.energy_infrastructure_tier = result.infrastructure_tier.value
        assert company.energy_trading_score is not None
