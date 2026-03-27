"""Tests for STORY-152: Grid Integration & Smart Infrastructure Scoring.

Validates the GridInfrastructureScorer against known advanced vs.
basic energy grid infrastructure profiles.
"""

from __future__ import annotations

import pytest

from solstein.analytics.energy_grid_infrastructure import (
    GridInfrastructureResult,
    GridInfrastructureScorer,
    GridReadiness,
    SmartInfraLevel,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_company(**overrides):  # type: ignore[no-untyped-def]
    """Create a minimal Company for testing."""
    from solstein.domain.models import Company

    defaults = {
        "id": "grid-test-001",
        "name": "GridCorp",
        "industry": "Energy Software",
        "revenue": 10_000_000,
        "employees": 150,
    }
    defaults.update(overrides)
    return Company(**defaults)


@pytest.fixture
def scorer() -> GridInfrastructureScorer:
    return GridInfrastructureScorer()


# ---------------------------------------------------------------------------
# TestResultStructure
# ---------------------------------------------------------------------------

class TestResultStructure:
    """Verify the grid result has all required fields."""

    def test_returns_result(self, scorer: GridInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert isinstance(result, GridInfrastructureResult)

    def test_has_three_dimension_scores(self, scorer: GridInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert 0 <= result.grid_connectivity_score <= 100
        assert 0 <= result.smart_infrastructure_score <= 100
        assert 0 <= result.decentralization_score <= 100

    def test_has_composite_score(self, scorer: GridInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert 0 <= result.composite_score <= 100

    def test_has_grid_readiness(self, scorer: GridInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert isinstance(result.grid_readiness, GridReadiness)

    def test_has_smart_level(self, scorer: GridInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert isinstance(result.smart_infra_level, SmartInfraLevel)

    def test_has_breakdown(self, scorer: GridInfrastructureScorer) -> None:
        result = scorer.score(_make_company())
        assert "grid_weight" in result.breakdown
        assert "smart_weight" in result.breakdown
        assert "decentralization_weight" in result.breakdown


# ---------------------------------------------------------------------------
# TestGridConnectivity
# ---------------------------------------------------------------------------

class TestGridConnectivity:
    """Verify grid connectivity scoring."""

    def test_grid_keywords_boost(self, scorer: GridInfrastructureScorer) -> None:
        basic = _make_company(description="Basic energy company")
        grid = _make_company(
            description="DER management with grid integration and frequency regulation"
        )
        r_basic = scorer.score(basic)
        r_grid = scorer.score(grid)
        assert r_grid.grid_connectivity_score > r_basic.grid_connectivity_score

    def test_der_boosts_score(self, scorer: GridInfrastructureScorer) -> None:
        basic = _make_company(description="Basic energy")
        der = _make_company(
            description="Solar inverter battery inverter with net metering and curtailment"
        )
        r_basic = scorer.score(basic)
        r_der = scorer.score(der)
        assert r_der.grid_connectivity_score > r_basic.grid_connectivity_score

    def test_vpp_boosts_score(self, scorer: GridInfrastructureScorer) -> None:
        basic = _make_company(description="Basic energy")
        vpp = _make_company(
            description="Virtual power plant with demand response and flexibility"
        )
        r_basic = scorer.score(basic)
        r_vpp = scorer.score(vpp)
        assert r_vpp.grid_connectivity_score > r_basic.grid_connectivity_score


# ---------------------------------------------------------------------------
# TestSmartInfrastructure
# ---------------------------------------------------------------------------

class TestSmartInfrastructure:
    """Verify smart infrastructure scoring."""

    def test_iot_boosts_score(self, scorer: GridInfrastructureScorer) -> None:
        basic = _make_company(description="Basic energy")
        iot = _make_company(
            description="IoT sensor network with smart meter and edge computing telemetry"
        )
        r_basic = scorer.score(basic)
        r_iot = scorer.score(iot)
        assert r_iot.smart_infrastructure_score > r_basic.smart_infrastructure_score

    def test_digital_twin_boosts_score(self, scorer: GridInfrastructureScorer) -> None:
        basic = _make_company(description="Basic energy")
        twin = _make_company(
            description="Digital twin with predictive maintenance"
        )
        r_basic = scorer.score(basic)
        r_twin = scorer.score(twin)
        assert r_twin.smart_infrastructure_score > r_basic.smart_infrastructure_score

    def test_ai_grid_boosts_score(self, scorer: GridInfrastructureScorer) -> None:
        basic = _make_company(description="Basic energy")
        ai = _make_company(
            description="Machine learning for load forecasting and anomaly detection"
        )
        r_basic = scorer.score(basic)
        r_ai = scorer.score(ai)
        assert r_ai.smart_infrastructure_score > r_basic.smart_infrastructure_score

    def test_ai_maturity_boosts_score(self, scorer: GridInfrastructureScorer) -> None:
        low = _make_company(description="Basic energy", ai_maturity="None")
        high = _make_company(description="Basic energy", ai_maturity="Strong")
        r_low = scorer.score(low)
        r_high = scorer.score(high)
        assert r_high.smart_infrastructure_score > r_low.smart_infrastructure_score

    def test_intelligent_level(self, scorer: GridInfrastructureScorer) -> None:
        company = _make_company(
            description=(
                "IoT sensor smart meter edge computing with "
                "digital twin predictive maintenance and "
                "machine learning load forecasting anomaly detection"
            ),
            ai_maturity="Strong",
        )
        result = scorer.score(company)
        assert result.smart_infra_level == SmartInfraLevel.INTELLIGENT


# ---------------------------------------------------------------------------
# TestDecentralization
# ---------------------------------------------------------------------------

class TestDecentralization:
    """Verify decentralization scoring."""

    def test_microgrid_boosts_score(self, scorer: GridInfrastructureScorer) -> None:
        basic = _make_company(description="Basic energy")
        micro = _make_company(
            description="Microgrid with island mode and community energy"
        )
        r_basic = scorer.score(basic)
        r_micro = scorer.score(micro)
        assert r_micro.decentralization_score > r_basic.decentralization_score

    def test_p2p_boosts_score(self, scorer: GridInfrastructureScorer) -> None:
        basic = _make_company(description="Basic energy")
        p2p = _make_company(
            description="Peer-to-peer prosumer energy marketplace"
        )
        r_basic = scorer.score(basic)
        r_p2p = scorer.score(p2p)
        assert r_p2p.decentralization_score > r_basic.decentralization_score

    def test_advanced_grid_readiness(self, scorer: GridInfrastructureScorer) -> None:
        company = _make_company(
            description=(
                "DER management grid integration frequency regulation "
                "virtual power plant demand response flexibility "
                "microgrid island mode community energy "
                "peer-to-peer prosumer energy marketplace"
            ),
        )
        result = scorer.score(company)
        assert result.grid_readiness == GridReadiness.ADVANCED


# ---------------------------------------------------------------------------
# TestRecommendations
# ---------------------------------------------------------------------------

class TestRecommendations:
    """Verify recommendations generation."""

    def test_basic_has_recommendations(self, scorer: GridInfrastructureScorer) -> None:
        company = _make_company(description="A basic energy company")
        result = scorer.score(company)
        assert len(result.recommendations) > 0

    def test_advanced_has_fewer_gaps(self, scorer: GridInfrastructureScorer) -> None:
        basic = _make_company(description="Basic company")
        advanced = _make_company(
            description=(
                "DER management grid integration virtual power plant "
                "demand response IoT sensor smart meter edge computing "
                "digital twin predictive maintenance machine learning "
                "microgrid island mode peer-to-peer prosumer"
            ),
            ai_maturity="Strong",
        )
        r_basic = scorer.score(basic)
        r_advanced = scorer.score(advanced)
        assert len(r_advanced.gaps) < len(r_basic.gaps)


# ---------------------------------------------------------------------------
# TestCompanyModelIntegration
# ---------------------------------------------------------------------------

class TestCompanyModelIntegration:
    """Verify Company model has grid infrastructure fields."""

    def test_company_has_grid_fields(self) -> None:
        company = _make_company()
        assert hasattr(company, "energy_grid_score")
        assert hasattr(company, "energy_grid_readiness")
        assert hasattr(company, "energy_smart_infra_level")
        assert hasattr(company, "energy_grid_breakdown")

    def test_store_grid_results(self, scorer: GridInfrastructureScorer) -> None:
        company = _make_company(
            description="DER management with microgrid"
        )
        result = scorer.score(company)
        company.energy_grid_score = result.composite_score
        company.energy_grid_readiness = result.grid_readiness.value
        company.energy_smart_infra_level = result.smart_infra_level.value
        assert company.energy_grid_score is not None
