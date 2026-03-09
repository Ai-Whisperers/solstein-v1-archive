from solstein.data_sources.openclaw_evaluator import OpenClawAPI, OpenClawEvaluator


def test_evaluator_scores_high_relevance_job_signal_api() -> None:
    evaluator = OpenClawEvaluator()
    api = OpenClawAPI(
        name="Hiring Signals API",
        category="jobs",
        endpoint="/global/hiring/signals",
        auth="api_key",
        rate_limit_per_min=180,
    )

    result = evaluator.evaluate(api)

    assert result.category_match == 1.0
    assert result.ci_relevance == 1.0
    assert result.weighted_score >= 0.9


def test_rank_apis_orders_by_weighted_score_descending() -> None:
    evaluator = OpenClawEvaluator()
    apis = [
        OpenClawAPI(name="Generic API", category="misc", endpoint="/us/misc", auth="none", rate_limit_per_min=10),
        OpenClawAPI(
            name="Social Signal API",
            category="social",
            endpoint="/global/social",
            auth="api_key",
            rate_limit_per_min=120,
        ),
    ]

    ranked = evaluator.rank_apis(apis)

    assert len(ranked) == 2
    assert ranked[0].weighted_score >= ranked[1].weighted_score
    assert ranked[0].api.name == "Social Signal API"


def test_top_candidates_filters_by_min_score_and_limit() -> None:
    evaluator = OpenClawEvaluator()
    apis = [
        OpenClawAPI(
            name=f"Signal API {idx}", category="news", endpoint="/global/news", auth="api_key", rate_limit_per_min=60
        )
        for idx in range(30)
    ]

    top = evaluator.top_candidates(apis, limit=5, min_score=0.7)

    assert len(top) == 5
    assert all(candidate.weighted_score >= 0.7 for candidate in top)
