from __future__ import annotations

from dataclasses import dataclass

from loguru import logger

from ..analytics.completeness import CompletenessCalculator, DataQualityTier, completeness_calculator
from ..domain.models import Company
from ..infrastructure.refresh import RefreshStatus, raise_if_stale
from .gap_analyzer import analyze_company_gaps


@dataclass(frozen=True)
class GateReason:
    code: str
    message: str
    details: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


@dataclass(frozen=True)
class ReportGateResult:
    passed: bool
    reasons: list[GateReason]

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "reason_count": len(self.reasons),
            "reasons": [reason.to_dict() for reason in self.reasons],
        }


class ReportReleaseGate:
    def __init__(
        self,
        completeness: CompletenessCalculator | None = None,
        min_completeness_score: float = 50.0,
        min_confidence: float = 0.5,
        allow_synthetic: bool = False,
    ) -> None:
        self.completeness: CompletenessCalculator = completeness or completeness_calculator
        self.min_completeness_score: float = min_completeness_score
        self.min_confidence: float = min_confidence
        self.allow_synthetic: bool = allow_synthetic

    def evaluate(
        self,
        companies: list[Company],
        refresh_statuses: list[RefreshStatus] | None = None,
        min_readiness_score: float | None = None,
        evidence_readiness: float | None = None,
        contradiction_count: int | None = None,
        contradiction_limit: int | None = None,
    ) -> ReportGateResult:
        reasons: list[GateReason] = []

        if refresh_statuses is not None:
            try:
                raise_if_stale(refresh_statuses)
            except ValueError as exc:
                reasons.append(
                    GateReason(
                        code="stale_refresh",
                        message="Refresh metadata is stale",
                        details={"error": str(exc)},
                    )
                )

        if min_readiness_score is not None and evidence_readiness is not None:
            if evidence_readiness < min_readiness_score:
                reasons.append(
                    GateReason(
                        code="evidence_readiness",
                        message="Evidence readiness below threshold",
                        details={
                            "readiness": evidence_readiness,
                            "threshold": min_readiness_score,
                        },
                    )
                )

        if contradiction_limit is not None and contradiction_count is not None:
            if contradiction_count > contradiction_limit:
                reasons.append(
                    GateReason(
                        code="contradictions",
                        message="Contradiction count exceeds limit",
                        details={
                            "count": contradiction_count,
                            "limit": contradiction_limit,
                        },
                    )
                )

        for company in companies:
            if not self.allow_synthetic:
                data_source_type = getattr(company, "data_source_type", "unknown")
                if str(data_source_type).lower() in {"synthetic", "mixed"}:
                    reasons.append(
                        GateReason(
                            code="synthetic_data",
                            message="Synthetic or mixed data detected",
                            details={"company": company.name, "data_source_type": str(data_source_type)},
                        )
                    )

            gap_result = analyze_company_gaps(company, min_confidence=self.min_confidence)
            if not gap_result["is_ready"]:
                reasons.append(
                    GateReason(
                        code="gap_analysis",
                        message="Required fields missing or invalid",
                        details={
                            "company": company.name,
                            "unresolved": gap_result["field_states"],
                        },
                    )
                )

            completeness_score = self.completeness.calculate_completeness_score(company)
            tier = self.completeness.assign_tier(completeness_score)
            if completeness_score < self.min_completeness_score or tier == DataQualityTier.INSUFFICIENT:
                reasons.append(
                    GateReason(
                        code="completeness",
                        message="Completeness score below threshold",
                        details={
                            "company": company.name,
                            "score": completeness_score,
                            "tier": tier.value,
                            "threshold": self.min_completeness_score,
                        },
                    )
                )

        passed = len(reasons) == 0
        logger.info("Report release gate evaluated", passed=passed, reason_count=len(reasons))
        return ReportGateResult(passed=passed, reasons=reasons)

    def ensure_release_ready(
        self,
        companies: list[Company],
        refresh_statuses: list[RefreshStatus] | None = None,
        min_readiness_score: float | None = None,
        evidence_readiness: float | None = None,
        contradiction_count: int | None = None,
        contradiction_limit: int | None = None,
    ) -> None:
        result = self.evaluate(
            companies=companies,
            refresh_statuses=refresh_statuses,
            min_readiness_score=min_readiness_score,
            evidence_readiness=evidence_readiness,
            contradiction_count=contradiction_count,
            contradiction_limit=contradiction_limit,
        )
        if not result.passed:
            raise ValueError("Report release gate failed: " + "; ".join(reason.code for reason in result.reasons))
