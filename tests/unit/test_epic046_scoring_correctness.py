import pytest
from types import SimpleNamespace

from solstein.analytics.constants import derive_threat_level
from solstein.analytics.scorers.competitive_position import CompetitivePositionScorer


@pytest.mark.parametrize(
    ("classification", "composite_score", "expected"),
    [
        ("Phoenix", 9.2, "Critical"),
        ("Phoenix", 7.4, "High"),
        ("Salt", 6.1, "Medium"),
        ("Salt", 5.9, "Low"),
        ("Lead", 8.7, "Low"),
    ],
)
def test_story173_threat_level_mapping(classification, composite_score, expected):
    assert derive_threat_level(classification, composite_score) == expected


def test_story174_competitive_position_handles_missing_saas_maturity():
    scorer = CompetitivePositionScorer()
    company = SimpleNamespace(
        id="cmp-null-saas",
        ai_maturity="Starter",
        tier="Contender",
        saas_maturity=None,
        geographic_presence=[],
        technologies_used=[],
        tech_stack=[],
    )

    score, explanation = scorer.score(company)

    assert 0.0 <= score <= 10.0
    saas_components = [component for component in explanation.components if component.name == "SaaS Maturity"]
    assert len(saas_components) == 1
    assert "5.0" in saas_components[0].formula
