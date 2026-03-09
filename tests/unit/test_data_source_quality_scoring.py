from solstein.data_sources.quality import QualityScorer, SourceQualityScores


def test_calculate_overall_uses_expected_weights() -> None:
    scorer = QualityScorer()
    scores = SourceQualityScores(
        reliability=0.9,
        freshness=0.8,
        coverage=0.7,
        accuracy=0.6,
        overall=0.0,
    )

    overall = scorer.calculate_overall(scores)

    assert overall == 0.78


def test_with_computed_overall_bounds_input_scores() -> None:
    scorer = QualityScorer()
    scores = scorer.with_computed_overall(
        reliability=1.4,
        freshness=-0.5,
        coverage=0.6,
        accuracy=0.5,
        sample_size=42,
        calculation_period_days=14,
    )

    assert scores.reliability == 1.0
    assert scores.freshness == 0.0
    assert scores.coverage == 0.6
    assert scores.accuracy == 0.5
    assert scores.sample_size == 42
    assert scores.calculation_period_days == 14
    assert 0.0 <= scores.overall <= 1.0


def test_with_computed_overall_preserves_dimension_factors() -> None:
    scorer = QualityScorer()
    scores = scorer.with_computed_overall(
        reliability=0.92,
        freshness=0.81,
        coverage=0.77,
        accuracy=0.88,
        reliability_factors={"uptime_percentage": 99.5},
        freshness_factors={"avg_data_age_hours": 12},
        coverage_factors={"fill_rate": 0.86},
        accuracy_factors={"validation_pass_rate": 0.95},
    )

    assert scores.reliability_factors["uptime_percentage"] == 99.5
    assert scores.freshness_factors["avg_data_age_hours"] == 12
    assert scores.coverage_factors["fill_rate"] == 0.86
    assert scores.accuracy_factors["validation_pass_rate"] == 0.95
    assert scores.overall > 0.0
