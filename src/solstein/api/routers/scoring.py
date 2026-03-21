import asyncio
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from loguru import logger
from pydantic import BaseModel

from solstein.analytics.classification_service import ClassificationService
from solstein.analytics.company_loader import unified_score_loader
from solstein.analytics.constants import PHOENIX_SCORE_THRESHOLD, SALT_SCORE_THRESHOLD
from solstein.analytics.scoring import GrowthScorer
from solstein.api.dependencies import get_company_repository, get_current_tenant
from solstein.api.exceptions import APIError
from solstein.config import get_settings
from solstein.data.adjudication import AdjudicationDecision, record_adjudication_decision
from solstein.data.report_release_gate import ReportReleaseGate

router = APIRouter(tags=["Scoring"])
growth_scorer = GrowthScorer()
classification_service = ClassificationService()


def _legacy_classification_from_growth(growth_score: float) -> str:
    if growth_score >= PHOENIX_SCORE_THRESHOLD:
        return "Phoenix"
    if growth_score < SALT_SCORE_THRESHOLD:
        return "Lead"
    return "Salt"


class AdjudicationRequest(BaseModel):
    metric: str
    decision: str
    actor: str
    reason: str
    status: str = "approved"
    value: Any = None


@router.post("/company/{company_id}/score")
async def score_company(
    company_id: str,
    _: dict[str, Any] = Depends(get_current_tenant),
    repo: Any = Depends(get_company_repository),
) -> dict[str, Any]:
    try:
        target_company = await _load_company_for_scoring(company_id, repo)

        gate = ReportReleaseGate(min_confidence=0.6, allow_synthetic=False)
        gate_result = gate.evaluate([target_company])
        if not gate_result.passed:
            reason_codes = ", ".join(reason.code for reason in gate_result.reasons)
            raise APIError(
                code="RELEASE_GATE_BLOCKED",
                message=f"Release gate blocked scoring: {reason_codes}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        scored_company = growth_scorer.calculate_scores(target_company)

        growth_score = scored_company.growth_score or 0.0
        classification, legacy_cls, canonical_cls = _determine_classification(growth_score, scored_company)

        await repo.save(scored_company)
        return _build_score_response(company_id, scored_company, classification, legacy_cls, canonical_cls)
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Error scoring company {company_id}: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error scoring company",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e


@router.post("/company/{company_id}/adjudicate")
async def adjudicate_company_claim(
    company_id: str,
    request: AdjudicationRequest,
    _: dict[str, Any] = Depends(get_current_tenant),
    repo: Any = Depends(get_company_repository),
) -> dict[str, Any]:
    try:
        target_company = await _load_company_for_scoring(company_id, repo)

        decision_id = f"{company_id}:{request.metric}:{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        decision = AdjudicationDecision(
            decision_id=decision_id,
            metric=request.metric,
            decision=request.decision,
            status=request.status,
            actor=request.actor,
            reason=request.reason,
            value=request.value,
            timestamp=datetime.now(UTC).isoformat(),
        )
        record_adjudication_decision(target_company, decision)
        await repo.save(target_company)

        gate = ReportReleaseGate(min_confidence=0.6, allow_synthetic=False)
        gate_result = gate.evaluate([target_company])

        return {
            "company_id": company_id,
            "decision_id": decision_id,
            "metric": request.metric,
            "decision": request.decision,
            "status": request.status,
            "gate_passed": gate_result.passed,
            "gate_reason_codes": sorted({reason.code for reason in gate_result.reasons}),
        }
    except APIError:
        raise
    except Exception as e:
        logger.error(f"Error adjudicating company {company_id}: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error adjudicating company claim",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e


@router.get("/batch")
async def batch_score_companies_endpoint(
    industry: str | None = Query(None, description="Industry to score"),
    min_revenue: float | None = Query(None, ge=0, description="Minimum revenue"),
    _: dict[str, Any] = Depends(get_current_tenant),
) -> dict[str, Any]:
    raise APIError(
        code="NOT_IMPLEMENTED",
        message=(
            "Batch scoring endpoint disabled - Temporal integration removed. "
            "Use individual /company/{id}/score endpoint instead."
        ),
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
    )


@router.get("/stats", tags=["Statistics"])
async def get_statistics(
    _: dict[str, Any] = Depends(get_current_tenant),
    repo: Any = Depends(get_company_repository),
) -> dict[str, Any]:
    try:
        companies = await repo.get_all()
        total_companies = len(companies)
        revenue_stats = _calculate_revenue_stats(companies)
        growth_stats = _calculate_growth_stats(companies)
        tier_counts, class_counts = _calculate_distributions(companies)

        return {
            "total_companies": total_companies,
            "revenue_statistics": revenue_stats,
            "growth_statistics": growth_stats,
            "tier_distribution": tier_counts,
            "growth_classification": class_counts,
            "calculated_at": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        raise APIError(
            code="INTERNAL_ERROR",
            message="Error calculating statistics",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(e),
        ) from e


async def _load_company_for_scoring(company_id: str, repo: Any) -> Any:
    target_company = await asyncio.to_thread(unified_score_loader.load_company_for_scoring, company_id)
    if not target_company:
        target_company = await repo.get_by_id(company_id)

    if not target_company:
        raise APIError(
            code="NOT_FOUND",
            message=f"Company with ID {company_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return target_company


def _determine_classification(
    growth_score: float,
    scored_company: Any,
) -> tuple[str, str, str]:
    legacy_classification = _legacy_classification_from_growth(growth_score)
    canonical_classification = scored_company.classification or classification_service.classify(
        scored_company.composite_score
    )

    settings = get_settings()
    use_new_classifier = settings.feature_new_classifier
    classification = canonical_classification if use_new_classifier else legacy_classification

    if legacy_classification != canonical_classification:
        logger.info(
            "Classification shadow mismatch",
            company_id=getattr(scored_company, "id", "unknown"),
            legacy=legacy_classification,
            canonical=canonical_classification,
            selected=classification,
            feature_new_classifier=use_new_classifier,
        )

    return classification, legacy_classification, canonical_classification


def _build_score_response(
    company_id: str,
    scored_company: Any,
    classification: str,
    legacy_classification: str,
    canonical_classification: str,
) -> dict[str, Any]:
    settings = get_settings()
    use_new_classifier = settings.feature_new_classifier

    return {
        "company_id": company_id,
        "growth_score": scored_company.growth_score,
        "financial_health_score": scored_company.financial_health_score,
        "competitive_position_score": scored_company.competitive_position_score,
        "composite_score": scored_company.composite_score,
        "classification": classification,
        "classification_shadow": {
            "legacy": legacy_classification,
            "canonical": canonical_classification,
            "selected": classification,
            "mismatch": legacy_classification != canonical_classification,
            "feature_new_classifier": use_new_classifier,
        },
        "scoring_breakdown": scored_company.scoring_breakdown,
        "calculated_at": datetime.now().isoformat(),
    }


def _calculate_revenue_stats(companies: list[Any]) -> dict[str, Any]:
    revenues = [c.financials.revenue for c in companies if c.financials and c.financials.revenue]
    total_revenue = sum(revenues) if revenues else 0
    avg_revenue = total_revenue / len(revenues) if revenues else 0

    return {
        "total_revenue_eur_m": total_revenue,
        "average_revenue_eur_m": avg_revenue,
        "companies_with_revenue_data": len(revenues),
    }


def _calculate_growth_stats(companies: list[Any]) -> dict[str, Any]:
    growth_rates = [c.financials.growth_rate for c in companies if c.financials and c.financials.growth_rate]
    avg_growth = sum(growth_rates) / len(growth_rates) if growth_rates else 0

    return {
        "average_growth_rate_pct": avg_growth,
        "companies_with_growth_data": len(growth_rates),
    }


def _calculate_distributions(companies: list[Any]) -> tuple[dict[str, int], dict[str, int]]:
    tier_counts: dict[str, int] = {}
    class_counts: dict[str, int] = {}

    for company in companies:
        raw_tier = company.tier
        tier = raw_tier.value if hasattr(raw_tier, "value") else (raw_tier or "unknown")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

        cls_val = company.classification or "Salt"
        class_counts[cls_val] = class_counts.get(cls_val, 0) + 1

    return tier_counts, class_counts
