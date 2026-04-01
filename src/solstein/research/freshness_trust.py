"""
Freshness windows and evidence-aware export trust tiers.

STORY-229: Computes per-company trust tiers (gold, silver, bronze,
review-required) based on evidence count, source diversity, contradiction
flags, and field staleness. Provides freshness policy for volatile vs
static fields and export metadata generation.

Trust tier rubric:
  gold            - 3+ sources, no major contradictions, all key fields fresh
  silver          - 2+ sources, no critical contradictions, most key fields present
  bronze          - 1 source or minor contradictions or some stale fields
  review-required - critical contradictions, or no evidence, or majority stale
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from loguru import logger

# ---------------------------------------------------------------------------
# Trust tier enum
# ---------------------------------------------------------------------------


class TrustTier(Enum):
    """Evidence-based trust classification for exported records."""

    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    REVIEW_REQUIRED = "review-required"


# ---------------------------------------------------------------------------
# Freshness policy
# ---------------------------------------------------------------------------

# Volatile fields change frequently and have shorter freshness windows
VOLATILE_FIELDS: set[str] = {
    "revenue",
    "revenue_growth",
    "employee_count",
    "funding_total",
    "latest_funding_round",
    "latest_funding_date",
    "latest_funding_amount",
    "stock_price",
    "market_cap",
    "quarterly_revenue",
    "burn_rate",
    "runway_months",
}

# Static fields rarely change and have longer freshness windows
STATIC_FIELDS: set[str] = {
    "company_name",
    "website",
    "industry",
    "founded_year",
    "headquarters",
    "description",
    "ceo",
    "founders",
    "business_model",
    "target_market",
}

# Freshness windows in hours
VOLATILE_FRESHNESS_HOURS = 24 * 7  # 7 days
STATIC_FRESHNESS_HOURS = 24 * 30 * 3  # ~90 days

# Key fields that must be present for higher tiers
KEY_FIELDS: set[str] = {
    "company_name",
    "website",
    "industry",
    "revenue",
    "employee_count",
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FreshnessResult:
    """Result of a field freshness check."""

    field_name: str
    is_stale: bool
    age_hours: float
    max_age_hours: float


@dataclass(frozen=True)
class TrustAssessment:
    """Complete trust assessment for a company record."""

    tier: TrustTier
    reasons: list[str]
    stale_fields: list[str]
    source_count: int
    contradiction_count: int
    key_field_coverage: float


# ---------------------------------------------------------------------------
# Freshness checking
# ---------------------------------------------------------------------------


def classify_field_volatility(field_name: str) -> str:
    """Classify a field as volatile, static, or unknown."""
    if field_name in VOLATILE_FIELDS:
        return "volatile"
    if field_name in STATIC_FIELDS:
        return "static"
    return "unknown"


def get_freshness_window(field_name: str) -> float:
    """Get the freshness window in hours for a field."""
    volatility = classify_field_volatility(field_name)
    if volatility == "volatile":
        return VOLATILE_FRESHNESS_HOURS
    if volatility == "static":
        return STATIC_FRESHNESS_HOURS
    # Unknown fields use volatile window as conservative default
    return VOLATILE_FRESHNESS_HOURS


def check_field_freshness(
    field_name: str,
    timestamp_iso: str,
    now: datetime | None = None,
) -> FreshnessResult:
    """Check if a field value is stale based on its freshness window.

    Args:
        field_name: The field to check.
        timestamp_iso: ISO-format timestamp of when the field was last updated.
        now: Current time (defaults to UTC now).

    Returns:
        FreshnessResult with staleness determination.
    """
    if now is None:
        now = datetime.now(timezone.utc)

    max_age = get_freshness_window(field_name)

    try:
        ts = datetime.fromisoformat(timestamp_iso.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age_hours = (now - ts).total_seconds() / 3600.0
    except (ValueError, AttributeError) as exc:
        logger.warning(f"[Freshness] Bad timestamp for {field_name}: {exc}")
        return FreshnessResult(
            field_name=field_name,
            is_stale=True,
            age_hours=float("inf"),
            max_age_hours=max_age,
        )

    return FreshnessResult(
        field_name=field_name,
        is_stale=age_hours > max_age,
        age_hours=round(age_hours, 1),
        max_age_hours=max_age,
    )


# ---------------------------------------------------------------------------
# Trust tier computation
# ---------------------------------------------------------------------------


def _count_unique_sources(runs: list[dict[str, Any]]) -> int:
    """Count unique source URLs across all runs."""
    sources: set[str] = set()
    for run in runs:
        if not isinstance(run, dict):
            continue
        for url in run.get("sources_used", []):
            if isinstance(url, str) and url:
                sources.add(url)
    return len(sources)


def _count_contradictions(
    runs: list[dict[str, Any]],
) -> tuple[int, int, int]:
    """Count contradiction flags by severity across latest run.

    Returns:
        (minor_count, major_count, critical_count)
    """
    minor = major = critical = 0
    if not runs:
        return minor, major, critical

    latest = runs[-1] if isinstance(runs[-1], dict) else {}
    evidence = latest.get("field_evidence", {})
    if not isinstance(evidence, dict):
        return minor, major, critical

    for field_ev in evidence.values():
        if not isinstance(field_ev, dict):
            continue
        for flag in field_ev.get("contradiction_flags", []):
            if not isinstance(flag, dict):
                continue
            severity = flag.get("severity", "")
            if severity == "critical":
                critical += 1
            elif severity == "major":
                major += 1
            elif severity == "minor":
                minor += 1

    return minor, major, critical


def _compute_key_field_coverage(
    latest_run: dict[str, Any],
) -> float:
    """Compute fraction of KEY_FIELDS that have a winner value."""
    if not latest_run or not isinstance(latest_run, dict):
        return 0.0

    evidence = latest_run.get("field_evidence", {})
    if not isinstance(evidence, dict):
        return 0.0

    if not KEY_FIELDS:
        return 0.0

    found = 0
    for kf in KEY_FIELDS:
        field_ev = evidence.get(kf)
        if not isinstance(field_ev, dict):
            continue
        winner = field_ev.get("winner")
        if isinstance(winner, dict) and winner.get("value") is not None:
            found += 1

    return found / len(KEY_FIELDS)


def _find_stale_fields(
    latest_run: dict[str, Any],
    now: datetime | None = None,
) -> list[str]:
    """Find fields in the latest run that are stale."""
    if not latest_run or not isinstance(latest_run, dict):
        return []

    run_timestamp = latest_run.get("timestamp", "")
    evidence = latest_run.get("field_evidence", {})
    if not isinstance(evidence, dict):
        return []

    stale: list[str] = []
    for field_name, field_ev in evidence.items():
        if not isinstance(field_ev, dict):
            continue
        winner = field_ev.get("winner")
        if not isinstance(winner, dict):
            continue

        # Use extraction_timestamp if available, fall back to run timestamp
        ts = winner.get("extraction_timestamp", run_timestamp)
        if not isinstance(ts, str) or not ts:
            ts = run_timestamp

        result = check_field_freshness(field_name, ts, now=now)
        if result.is_stale:
            stale.append(field_name)

    return sorted(stale)


@dataclass(frozen=True)
class _EvidenceMetrics:
    """Internal: aggregated evidence metrics for tier decision."""

    source_count: int
    minor_contradictions: int
    major_contradictions: int
    critical_contradictions: int
    total_contradictions: int
    coverage: float
    stale_fields: list[str]
    total_fields: int
    latest_run: dict[str, Any]


def _gather_evidence_metrics(
    runs: list[dict[str, Any]],
    now: datetime | None,
) -> _EvidenceMetrics:
    """Gather all evidence metrics needed for tier decision."""
    latest_run = runs[-1] if isinstance(runs[-1], dict) else {}
    source_count = _count_unique_sources(runs)
    minor_c, major_c, critical_c = _count_contradictions(runs)
    coverage = _compute_key_field_coverage(latest_run)
    stale = _find_stale_fields(latest_run, now=now)
    evidence = latest_run.get("field_evidence", {})
    total_fields = len(evidence) if isinstance(evidence, dict) else 0

    return _EvidenceMetrics(
        source_count=source_count,
        minor_contradictions=minor_c,
        major_contradictions=major_c,
        critical_contradictions=critical_c,
        total_contradictions=minor_c + major_c + critical_c,
        coverage=coverage,
        stale_fields=stale,
        total_fields=total_fields,
        latest_run=latest_run,
    )


def _check_review_required(m: _EvidenceMetrics) -> list[str] | None:
    """Check if metrics warrant review-required tier. Returns reasons or None."""
    if m.critical_contradictions > 0:
        return [f"{m.critical_contradictions} critical contradiction(s)"]
    if m.source_count == 0:
        return ["no source URLs recorded"]
    if m.total_fields > 0 and len(m.stale_fields) > m.total_fields * 0.5:
        return [f"{len(m.stale_fields)}/{m.total_fields} fields stale"]
    return None


def _check_gold(m: _EvidenceMetrics) -> bool:
    """Check if metrics qualify for gold tier."""
    return m.source_count >= 3 and m.major_contradictions == 0 and m.coverage >= 1.0 and len(m.stale_fields) == 0


def _build_silver_reasons(m: _EvidenceMetrics) -> list[str]:
    """Build reason list for silver tier."""
    reasons: list[str] = []
    if m.major_contradictions > 0:
        reasons.append(f"{m.major_contradictions} major contradiction(s)")
    if len(m.stale_fields) > 0:
        reasons.append(f"{len(m.stale_fields)} stale field(s)")
    if m.coverage < 1.0:
        reasons.append(f"key field coverage {m.coverage:.0%}")
    if not reasons:
        reasons.append("adequate evidence with minor gaps")
    return reasons


def _build_bronze_reasons(m: _EvidenceMetrics) -> list[str]:
    """Build reason list for bronze tier."""
    reasons: list[str] = []
    if m.source_count == 1:
        reasons.append("single source only")
    if m.major_contradictions > 0:
        reasons.append(f"{m.major_contradictions} major contradiction(s)")
    if m.minor_contradictions > 0:
        reasons.append(f"{m.minor_contradictions} minor contradiction(s)")
    if len(m.stale_fields) > 0:
        reasons.append(f"{len(m.stale_fields)} stale field(s)")
    if m.coverage < 0.6:
        reasons.append(f"low key field coverage {m.coverage:.0%}")
    if not reasons:
        reasons.append("limited evidence")
    return reasons


def _make_assessment(
    tier: TrustTier,
    reasons: list[str],
    m: _EvidenceMetrics,
) -> TrustAssessment:
    """Build a TrustAssessment from tier, reasons, and metrics."""
    return TrustAssessment(
        tier=tier,
        reasons=reasons,
        stale_fields=m.stale_fields,
        source_count=m.source_count,
        contradiction_count=m.total_contradictions,
        key_field_coverage=m.coverage,
    )


def compute_trust_tier(
    company_entry: dict[str, Any],
    now: datetime | None = None,
) -> TrustAssessment:
    """Compute trust tier for a company based on evidence quality.

    Args:
        company_entry: Company dict with optional "runs" list.
        now: Current time for freshness checks.

    Returns:
        TrustAssessment with tier, reasons, and quality metrics.
    """
    runs = company_entry.get("runs", [])
    if not isinstance(runs, list) or not runs:
        return TrustAssessment(
            tier=TrustTier.REVIEW_REQUIRED,
            reasons=["no evidence runs found"],
            stale_fields=[],
            source_count=0,
            contradiction_count=0,
            key_field_coverage=0.0,
        )

    m = _gather_evidence_metrics(runs, now)

    # Check review-required conditions first
    review_reasons = _check_review_required(m)
    if review_reasons is not None:
        return _make_assessment(TrustTier.REVIEW_REQUIRED, review_reasons, m)

    # Gold tier
    if _check_gold(m):
        return _make_assessment(
            TrustTier.GOLD,
            ["well-evidenced across multiple sources"],
            m,
        )

    # Silver tier: 2+ sources, decent coverage
    if m.source_count >= 2 and m.coverage >= 0.6:
        return _make_assessment(
            TrustTier.SILVER,
            _build_silver_reasons(m),
            m,
        )

    # Bronze: everything else
    return _make_assessment(
        TrustTier.BRONZE,
        _build_bronze_reasons(m),
        m,
    )


# ---------------------------------------------------------------------------
# Export metadata
# ---------------------------------------------------------------------------


def build_export_metadata(
    assessment: TrustAssessment,
) -> dict[str, Any]:
    """Build export-ready metadata dict from a TrustAssessment."""
    return {
        "trust_tier": assessment.tier.value,
        "trust_reasons": assessment.reasons,
        "stale_fields": assessment.stale_fields,
        "source_count": assessment.source_count,
        "contradiction_count": assessment.contradiction_count,
        "key_field_coverage": round(assessment.key_field_coverage, 2),
    }


def assess_and_export(
    company_entry: dict[str, Any],
    now: datetime | None = None,
) -> dict[str, Any]:
    """Convenience: compute trust tier and return export metadata."""
    assessment = compute_trust_tier(company_entry, now=now)
    return build_export_metadata(assessment)


__all__ = [
    "TrustTier",
    "VOLATILE_FIELDS",
    "STATIC_FIELDS",
    "KEY_FIELDS",
    "VOLATILE_FRESHNESS_HOURS",
    "STATIC_FRESHNESS_HOURS",
    "FreshnessResult",
    "TrustAssessment",
    "classify_field_volatility",
    "get_freshness_window",
    "check_field_freshness",
    "compute_trust_tier",
    "build_export_metadata",
    "assess_and_export",
]
