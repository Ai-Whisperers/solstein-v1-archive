from solstein.analytics.scoring import GrowthScorer
from solstein.core.scoring_config import ScoringSettings
from tests.factories import make_company


def test_composite_score_uses_configured_weights() -> None:
    config = ScoringSettings()
    config.composite.growth_weight = 0.2
    config.composite.financial_weight = 0.5
    config.composite.competitive_weight = 0.3

    scorer = GrowthScorer(config=config)
    company = make_company()
    scored = scorer.calculate_scores(company)

    assert scored.growth_score is not None
    assert scored.financial_health_score is not None
    assert scored.competitive_position_score is not None
    assert scored.composite_score is not None

    expected = round(
        (scored.growth_score * 0.2) + (scored.financial_health_score * 0.5) + (scored.competitive_position_score * 0.3),
        2,
    )
    assert scored.composite_score == expected
