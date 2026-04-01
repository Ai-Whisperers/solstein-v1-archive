"""Tests for STORY-148: Transformation Roadmap Generator.

Validates the RoadmapGenerator against energy sector patterns,
phase structure, industry customisation, and edge cases.
"""

from __future__ import annotations

import pytest

from solstein.application.roadmap_generator import (
    RoadmapGenerator,
    TransformationRoadmap,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_company(**overrides):  # type: ignore[no-untyped-def]
    """Create a minimal Company for testing."""
    from solstein.domain.models import Company

    defaults = {
        "id": "roadmap-test-001",
        "name": "RoadmapCorp",
        "industry": "Energy Software",
        "revenue": 10_000_000,
        "employees": 150,
    }
    defaults.update(overrides)
    return Company(**defaults)


@pytest.fixture
def generator() -> RoadmapGenerator:
    return RoadmapGenerator()


# ---------------------------------------------------------------------------
# TestRoadmapStructure
# ---------------------------------------------------------------------------

class TestRoadmapStructure:
    """Verify the roadmap contains all 4 required phases."""

    def test_returns_transformation_roadmap(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        assert isinstance(result, TransformationRoadmap)

    def test_has_four_phases(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        assert len(result.phases) == 4

    def test_phase_names(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        names = [p.name for p in result.phases]
        assert names == ["Foundation", "Quick Wins", "Transformation", "Optimisation"]

    def test_phases_are_sequential(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        for i in range(len(result.phases) - 1):
            assert result.phases[i].end_month <= result.phases[i + 1].start_month + 1

    def test_each_phase_has_initiatives(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        for phase in result.phases:
            assert len(phase.initiatives) > 0, f"Phase '{phase.name}' has no initiatives"

    def test_total_investment_positive(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        assert result.total_investment_eur > 0

    def test_total_investment_is_sum_of_phases(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        phase_sum = sum(p.total_budget_eur for p in result.phases)
        assert result.total_investment_eur == phase_sum

    def test_executive_summary_present(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        assert result.executive_summary
        assert "RoadmapCorp" in result.executive_summary


# ---------------------------------------------------------------------------
# TestIndustryPatterns
# ---------------------------------------------------------------------------

class TestIndustryPatterns:
    """Verify industry-specific patterns are applied."""

    def test_energy_pattern(self, generator: RoadmapGenerator) -> None:
        company = _make_company(industry="Energy Software")
        result = generator.generate(company)
        assert result.industry == "energy"
        # Energy quick wins should include predictive maintenance
        qw_names = [i.name for p in result.phases if p.name == "Quick Wins" for i in p.initiatives]
        assert any("maintenance" in n.lower() or "regulatory" in n.lower() for n in qw_names)

    def test_fintech_pattern(self, generator: RoadmapGenerator) -> None:
        company = _make_company(industry="Fintech")
        result = generator.generate(company)
        assert result.industry == "fintech"
        qw_names = [i.name for p in result.phases if p.name == "Quick Wins" for i in p.initiatives]
        assert any("fraud" in n.lower() or "churn" in n.lower() for n in qw_names)

    def test_generic_pattern(self, generator: RoadmapGenerator) -> None:
        company = _make_company(industry="Healthcare")
        result = generator.generate(company)
        assert result.industry == "generic"

    def test_industry_recorded_in_customisations(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        assert any("energy" in c.lower() for c in result.customisations_applied)


# ---------------------------------------------------------------------------
# TestInitiativeQuality
# ---------------------------------------------------------------------------

class TestInitiativeQuality:
    """Verify initiatives have all required fields."""

    def test_initiatives_have_timeline(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        for phase in result.phases:
            for init in phase.initiatives:
                assert init.timeline_months, f"Initiative '{init.name}' missing timeline"

    def test_initiatives_have_success_metric(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        for phase in result.phases:
            for init in phase.initiatives:
                assert init.success_metric, f"Initiative '{init.name}' missing success metric"

    def test_initiatives_have_resources(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        for phase in result.phases:
            for init in phase.initiatives:
                assert init.resources, f"Initiative '{init.name}' missing resources"

    def test_initiatives_have_effort_impact(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company())
        for phase in result.phases:
            for init in phase.initiatives:
                assert init.effort in ("low", "medium", "high")
                assert init.impact in ("low", "medium", "high")


# ---------------------------------------------------------------------------
# TestCustomisation
# ---------------------------------------------------------------------------

class TestCustomisation:
    """Verify customisation overrides work."""

    def test_custom_foundation_budget(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(
            _make_company(),
            customisations={"foundation_budget": 500_000},
        )
        foundation = result.phases[0]
        assert foundation.total_budget_eur == 500_000

    def test_customisation_recorded(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(
            _make_company(),
            customisations={"foundation_budget": 500_000},
        )
        assert any("Custom" in c for c in result.customisations_applied)


# ---------------------------------------------------------------------------
# TestEdgeCases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Handle sparse data gracefully."""

    def test_minimal_company(self, generator: RoadmapGenerator) -> None:
        company = _make_company()
        result = generator.generate(company)
        assert len(result.phases) == 4

    def test_metadata_includes_maturity(self, generator: RoadmapGenerator) -> None:
        result = generator.generate(_make_company(saas_maturity=7, ai_maturity="Strong"))
        assert "ai_maturity" in result.metadata
        assert "saas_maturity" in result.metadata
