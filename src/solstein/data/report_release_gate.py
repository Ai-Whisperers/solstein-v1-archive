from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast

from loguru import logger

from ..analytics.completeness import CompletenessCalculator, DataQualityTier, completeness_calculator
from ..domain.models import Company
from ..infrastructure.refresh import RefreshStatus, raise_if_stale
from ..research.reconcile import detect_company_contradictions
from .gap_analyzer import analyze_company_gaps
from .provenance import validate_company_boundary_provenance

CRITICAL_CLAIM_FIELDS = {"revenue", "employee_count", "employees", "funding_total", "funding", "valuation"}


def _is_override_decision(decision: object) -> bool:
    if not isinstance(decision, Mapping):
        return False
    decision_map = cast(Mapping[str, object], decision)
    status = str(decision_map.get("status", "")).lower()
    decision_type = str(decision_map.get("decision", "")).lower()
    return status in {"approved", "override", "resolved"} or decision_type in {"approve", "override", "resolved"}


def _get_metric_adjudication(company: Company, metric: str) -> dict[str, object] | None:
    decisions_obj = getattr(company, "adjudication_decisions", {}) or {}
    if isinstance(decisions_obj, Mapping):
        decisions = cast(Mapping[str, object], decisions_obj)
        direct = decisions.get(metric)
        if isinstance(direct, Mapping):
            return dict(cast(Mapping[str, object], direct))

    aliases = {
        "employees": ("employee_count",),
        "employee_count": ("employees",),
        "funding": ("funding_total",),
        "funding_total": ("funding",),
    }
    for alias in aliases.get(metric, ()):
        if isinstance(decisions_obj, Mapping):
            candidate = cast(Mapping[str, object], decisions_obj).get(alias)
            if isinstance(candidate, Mapping):
                return dict(cast(Mapping[str, object], candidate))

    justifications_obj = getattr(company, "metric_justifications", {}) or {}
    if not isinstance(justifications_obj, Mapping):
        return None
    justifications = cast(Mapping[str, object], justifications_obj)

    keys = [f"adjudication:{metric}"] + [f"adjudication:{alias}" for alias in aliases.get(metric, ())]
    for key in keys:
        raw = justifications.get(key)
        if not isinstance(raw, str):
            continue
        parsed: dict[str, object] = {}
        for token in raw.split(";"):
            token = token.strip()
            if "=" not in token:
                continue
            name, value = token.split("=", 1)
            parsed[name.strip()] = value.strip()
        if parsed:
            return parsed
    return None


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
    skipped: bool = False
    warn_mode: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "skipped": self.skipped,
            "warn_mode": self.warn_mode,
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
        warn_mode: bool = False,
        skip_gate: bool = False,
    ) -> None:
        self.completeness: CompletenessCalculator = completeness or completeness_calculator
        self.min_completeness_score: float = min_completeness_score
        self.min_confidence: float = min_confidence
        self.allow_synthetic: bool = allow_synthetic
        self.warn_mode: bool = warn_mode
        self.skip_gate: bool = skip_gate

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

            boundary_violations = validate_company_boundary_provenance(
                company,
                min_confidence=self.min_confidence,
            )
            if boundary_violations:
                reasons.append(
                    GateReason(
                        code="provenance_boundary",
                        message="Populated fields missing required boundary provenance metadata",
                        details={
                            "company": company.name,
                            "violations": [
                                {
                                    "field": violation.field,
                                    "type": violation.violation_type,
                                    "message": violation.message,
                                }
                                for violation in boundary_violations
                            ],
                        },
                    )
                )

            contradictions = detect_company_contradictions(company)
            critical_contradictions = [
                contradiction
                for contradiction in contradictions
                if str(contradiction.get("metric", "")).lower() in CRITICAL_CLAIM_FIELDS
            ]
            if critical_contradictions:
                unresolved: list[dict[str, object]] = []
                resolved: list[dict[str, object]] = []
                for contradiction in critical_contradictions:
                    metric = str(contradiction.get("metric", "")).lower()
                    decision = _get_metric_adjudication(company, metric)
                    if decision is not None and _is_override_decision(decision):
                        resolved.append(
                            {
                                "metric": metric,
                                "decision_id": decision.get("decision_id"),
                                "decision": decision.get("decision"),
                                "status": decision.get("status"),
                            }
                        )
                    else:
                        unresolved.append(contradiction)

                if unresolved:
                    reasons.append(
                        GateReason(
                            code="critical_claim_contradiction",
                            message="Critical claims contain contradictory source observations",
                            details={
                                "company": company.name,
                                "count": len(unresolved),
                                "contradictions": unresolved,
                                "resolved_overrides": resolved,
                            },
                        )
                    )
                elif resolved:
                    reasons.append(
                        GateReason(
                            code="adjudication_override",
                            message="Critical contradictions resolved by adjudication decisions",
                            details={
                                "company": company.name,
                                "resolved_count": len(resolved),
                                "resolved_overrides": resolved,
                            },
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

        blocking_codes = {reason.code for reason in reasons if reason.code != "adjudication_override"}
        passed = len(blocking_codes) == 0
        logger.info("Report release gate evaluated", passed=passed, reason_count=len(reasons))

        if self.skip_gate:
            logger.warning("Report release gate skipped", reason_count=len(reasons))
            return ReportGateResult(passed=True, reasons=reasons, skipped=True, warn_mode=False)

        if self.warn_mode and reasons:
            for reason in reasons:
                logger.warning(f"WARNING: {reason.code} - {reason.message}")
            return ReportGateResult(passed=True, reasons=reasons, skipped=False, warn_mode=True)

        return ReportGateResult(passed=passed, reasons=reasons, skipped=False, warn_mode=False)

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


def determine_quality_tier(result: ReportGateResult) -> str:
    blocking_codes = {reason.code for reason in result.reasons if reason.code != "adjudication_override"}
    if not blocking_codes:
        return "gold"
    if blocking_codes == {"completeness"}:
        return "silver"
    if len(blocking_codes) <= 2:
        return "bronze"
    return "warning"


def calculate_completeness_score(
    companies: list[Company],
    completeness: CompletenessCalculator | None = None,
) -> float:
    calculator = completeness or completeness_calculator
    if not companies:
        return 0.0
    scores = [calculator.calculate_completeness_score(company) for company in companies]
    return round(sum(scores) / len(scores), 1)


def build_export_metadata(
    companies: list[Company],
    result: ReportGateResult,
    completeness: CompletenessCalculator | None = None,
) -> dict[str, object]:
    completeness_score = calculate_completeness_score(companies, completeness)
    metadata: dict[str, object] = {
        "gate_evaluation": result.to_dict(),
        "data_quality_tier": determine_quality_tier(result),
        "completeness_score": completeness_score,
    }
    try:
        json.dumps(metadata)
    except TypeError as exc:
        logger.error(f"Failed to serialize export metadata: {exc}")
        raise
    return metadata
