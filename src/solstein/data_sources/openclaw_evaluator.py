from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OpenClawAPI:
    name: str
    category: str
    endpoint: str
    auth: str
    rate_limit_per_min: int | None = None


@dataclass(frozen=True)
class OpenClawEvaluation:
    api: OpenClawAPI
    category_match: float
    ci_relevance: float
    technical_fit: float
    coverage: float
    weighted_score: float


class OpenClawEvaluator:
    def __init__(self) -> None:
        self.weights = {
            "category_match": 0.35,
            "ci_relevance": 0.35,
            "technical_fit": 0.2,
            "coverage": 0.1,
        }

    def evaluate(self, api: OpenClawAPI) -> OpenClawEvaluation:
        category_match = self._score_category(api)
        ci_relevance = self._score_ci_relevance(api)
        technical_fit = self._score_technical_fit(api)
        coverage = self._score_coverage(api)

        weighted_score = (
            category_match * self.weights["category_match"]
            + ci_relevance * self.weights["ci_relevance"]
            + technical_fit * self.weights["technical_fit"]
            + coverage * self.weights["coverage"]
        )

        return OpenClawEvaluation(
            api=api,
            category_match=category_match,
            ci_relevance=ci_relevance,
            technical_fit=technical_fit,
            coverage=coverage,
            weighted_score=round(weighted_score, 4),
        )

    def rank_apis(self, apis: list[OpenClawAPI]) -> list[OpenClawEvaluation]:
        evaluations = [self.evaluate(api) for api in apis]
        return sorted(evaluations, key=lambda item: item.weighted_score, reverse=True)

    def top_candidates(
        self, apis: list[OpenClawAPI], limit: int = 20, min_score: float = 0.6
    ) -> list[OpenClawEvaluation]:
        ranked = self.rank_apis(apis)
        return [item for item in ranked if item.weighted_score >= min_score][:limit]

    def _score_category(self, api: OpenClawAPI) -> float:
        category = api.category.lower()
        if any(key in category for key in ("job", "hiring", "talent", "news", "social", "lead")):
            return 1.0
        if any(key in category for key in ("company", "market", "profile", "discovery")):
            return 0.7
        return 0.3

    def _score_ci_relevance(self, api: OpenClawAPI) -> float:
        name = api.name.lower()
        if any(key in name for key in ("news", "signal", "social", "hiring", "jobs")):
            return 1.0
        if any(key in name for key in ("company", "profile", "search")):
            return 0.75
        return 0.4

    def _score_technical_fit(self, api: OpenClawAPI) -> float:
        if api.auth.lower() in {"api_key", "bearer", "oauth2"}:
            auth_score = 1.0
        else:
            auth_score = 0.6

        if api.rate_limit_per_min is None:
            rate_score = 0.7
        elif api.rate_limit_per_min >= 120:
            rate_score = 1.0
        elif api.rate_limit_per_min >= 30:
            rate_score = 0.8
        else:
            rate_score = 0.5

        return round((auth_score + rate_score) / 2, 4)

    def _score_coverage(self, api: OpenClawAPI) -> float:
        endpoint = api.endpoint.lower()
        if any(key in endpoint for key in ("global", "multi", "international")):
            return 1.0
        if any(key in endpoint for key in ("us", "eu", "latam")):
            return 0.8
        return 0.6
