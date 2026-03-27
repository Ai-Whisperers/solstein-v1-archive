"""Company data conversion utilities.

EPIC-021: Extracted from loaders.py as part of file splitting.
EPIC-020: Refactored convert_to_domain_company from 432 lines to <100 lines.

Converts raw JSON data to Company domain entities.
"""

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from solstein.core.scoring_utils import populate_signal_confidences  # noqa: F401
from solstein.data.metric_contract import normalize_financial_payload
from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
)

from .company_extractors import (
    build_confidence_scores,
    build_enrichment_quality_metrics,
    build_metric_sources,
    convert_source_links,
    determine_ai_maturity,
    determine_data_quality_tier,
    determine_threat_level,
    extract_ai_data,
    extract_employee_data,
    extract_funding_data,
    extract_profitability_data,
    extract_revenue_data,
    extract_scorecard_data,
)

logger = logging.getLogger(__name__)


def determine_tier(revenue: float | None) -> CompanyTier:
    """Determine company tier based on revenue."""
    if revenue is None:
        return CompanyTier.TIER_4

    if revenue >= 1000:  # >= €1B
        return CompanyTier.TIER_1
    elif revenue >= 100:  # >= €100M
        return CompanyTier.TIER_2
    elif revenue >= 10:  # >= €10M
        return CompanyTier.TIER_3
    else:
        return CompanyTier.TIER_4


_FOLDER_KEYWORD_TO_HQ: list[tuple[tuple[str, ...], str]] = [
    (("uk", "british"), "United Kingdom"),
    (("german", "deutsch"), "Germany"),
    (("french", "france"), "France"),
    (("norway", "norwegian"), "Norway"),
    (("spain", "spanish"), "Spain"),
    (("poland", "polish"), "Poland"),
    (("swiss", "switzerland"), "Switzerland"),
]


def estimate_headquarters(folder: str) -> str | None:
    """Estimate headquarters based on folder name."""
    folder_lower = folder.lower()
    for keywords, country in _FOLDER_KEYWORD_TO_HQ:
        if any(kw in folder_lower for kw in keywords):
            return country
    return "Europe"


def _apply_signal_confidence_aliases(confidences: dict[str, float]) -> dict[str, float]:
    alias_map = {
        "revenue": ["revenue_level"],
        "employees": ["company_size"],
        "profit_margin": ["profitability"],
        "funding_raised": ["funding"],
        "funding": ["funding_raised"],
    }
    for source_key, alias_keys in alias_map.items():
        if source_key in confidences:
            for alias_key in alias_keys:
                confidences.setdefault(alias_key, confidences[source_key])
    return confidences


def _validate_conversion_loss(
    company_name: str,
    raw_values: dict[str, Any],
    normalized_values: dict[str, Any],
) -> None:
    present_raw = {key for key, value in raw_values.items() if value is not None}
    if not present_raw:
        return
    lost_fields = [key for key in present_raw if normalized_values.get(key) is None]
    loss_ratio = len(lost_fields) / len(present_raw)
    if loss_ratio > 0.3:
        logger.error(
            "[EPIC-059] Conversion lost %s/%s fields (%.0f%%) for %s. Lost fields: %s",
            len(lost_fields),
            len(present_raw),
            loss_ratio * 100,
            company_name,
            lost_fields,
        )


def extract_geographic_presence(raw_data: dict[str, Any]) -> list[str]:
    """Extract geographic presence from raw data."""
    # Check for flat format first (Ivan's simplified JSON)
    flat_presence = raw_data.get("geographic_presence")
    if isinstance(flat_presence, list) and flat_presence:
        return flat_presence

    # Original nested format
    geographic = raw_data.get("geographic", {})

    if not geographic or not isinstance(geographic, dict):
        return []

    # If major_offices are available, extract countries from them
    major_offices = geographic.get("major_offices", [])
    if major_offices:
        return major_offices[:3]

    # If headquarters is available, use it
    headquarters = geographic.get("headquarters")
    if headquarters:
        return [headquarters]

    return []


def _validate_financial_conversion(financial_metric: FinancialMetric, raw_data: dict[str, Any]) -> bool:
    """Validate that conversion didn't lose critical financial fields."""
    critical_fields = ["revenue", "employees", "growth_rate", "profit_margin", "funding_raised", "valuation"]
    expected_present = [f for f in critical_fields if f in raw_data and raw_data.get(f) is not None]
    actual_present = [f for f in critical_fields if getattr(financial_metric, f, None) is not None]

    if expected_present and actual_present:
        loss_rate = (len(expected_present) - len(actual_present)) / len(expected_present)
        if loss_rate > 0.30:
            logging.error(f"[EPIC-059] Conversion lost {loss_rate * 100:.1f}% of financial fields")
            return False
    return True


def _normalize_and_validate_financials(
    company_name: str,
    revenue_data: dict[str, Any],
    profitability_data: dict[str, Any],
    funding_data: dict[str, Any],
    employee_data: dict[str, Any],
) -> dict[str, Any]:
    """Normalize raw financial payload and validate conversion loss."""
    normalized = normalize_financial_payload(
        {
            "revenue": revenue_data["latest_revenue"],
            "growth_rate": revenue_data["latest_growth"],
            "profit_margin": profitability_data["profit_margin"],
            "funding_raised": funding_data["total_funding_eur"],
            "valuation": funding_data["latest_valuation_eur"],
        }
    )
    _validate_conversion_loss(
        company_name,
        {
            "revenue": revenue_data["latest_revenue"],
            "growth_rate": revenue_data["latest_growth"],
            "profit_margin": profitability_data["profit_margin"],
            "funding_raised": funding_data["total_funding_eur"],
            "valuation": funding_data["latest_valuation_eur"],
            "employees": employee_data["employee_count"],
        },
        {
            "revenue": normalized["revenue"],
            "growth_rate": normalized["growth_rate"],
            "profit_margin": normalized["profit_margin"],
            "funding_raised": normalized["funding_raised"],
            "valuation": normalized["valuation"],
            "employees": employee_data["employee_count"],
        },
    )
    return normalized


def _build_financial_metric(
    normalized_financials: dict[str, Any],
    revenue_data: dict[str, Any],
    profitability_data: dict[str, Any],
    employee_data: dict[str, Any],
) -> FinancialMetric:
    """Build FinancialMetric, supporting sparse companies with no revenue or employees.

    EPIC-058 / STORY-204: Sparse companies (e.g. Moixa, OVO Energy) may have neither
    revenue nor employees in the source JSON.  FinancialMetric's model_validator
    rejects that combination unless allow_empty_primary=True.
    """
    is_sparse = normalized_financials["revenue"] is None and employee_data["employee_count"] is None
    return FinancialMetric(
        allow_empty_primary=is_sparse,
        revenue=normalized_financials["revenue"],
        revenue_confidence=revenue_data["revenue_confidence"],
        growth_rate=normalized_financials["growth_rate"],
        growth_confidence=ConfidenceLevel.ESTIMATED
        if normalized_financials["growth_rate"]
        else ConfidenceLevel.UNKNOWN,
        employees=employee_data["employee_count"],
        employees_confidence=ConfidenceLevel.CONFIRMED if employee_data["employee_count"] else ConfidenceLevel.UNKNOWN,
        profit_margin=normalized_financials["profit_margin"],
        margin_confidence=ConfidenceLevel.CONFIRMED
        if normalized_financials["profit_margin"]
        else ConfidenceLevel.UNKNOWN,
        ebitda_margin=profitability_data["ebitda_margin"],
        recurring_revenue_pct=profitability_data["recurring_revenue_pct"],
        funding_raised=normalized_financials["funding_raised"],
        funding_confidence=ConfidenceLevel.ESTIMATED
        if normalized_financials["funding_raised"]
        else ConfidenceLevel.UNKNOWN,
        valuation=normalized_financials["valuation"],
        valuation_confidence=ConfidenceLevel.ESTIMATED
        if normalized_financials["valuation"]
        else ConfidenceLevel.UNKNOWN,
    )


def _derive_ai_score(
    ai_data: dict[str, Any],
    ai_maturity: AIMaturity,
    raw_data: dict[str, Any],
) -> float | None:
    """Derive AI score from maturity level when a direct score is absent."""
    ai_score = ai_data["ai_score"]
    if ai_score is None and any(
        [
            raw_data.get("ai_maturity"),
            ai_data["ai_signal_level"],
            ai_data["ai_capabilities"],
            ai_data["ai_in_production"],
        ]
    ):
        ai_score_by_maturity = {
            AIMaturity.STRONG: 8.0,
            AIMaturity.MODERATE: 6.0,
            AIMaturity.LOW: 3.0,
            AIMaturity.NONE: 1.0,
        }
        return ai_score_by_maturity.get(ai_maturity, 1.0)
    return ai_score


def convert_to_domain_company(raw_data: dict[str, Any], index: int = 0) -> Company:
    """Convert raw JSON data to Company domain entity.

    EPIC-020: Refactored from 432-line monolithic function.
    EPIC-058: Fixed to handle both flat and nested data formats.
    Now uses specialized extractor functions for each data domain.
    """
    # Basic info
    company_name = raw_data.get("company_name") or raw_data.get("name") or f"Company {index}"
    folder = raw_data.get("folder", f"company-{index}")

    # Extract data using specialized extractors
    revenue_data = extract_revenue_data(raw_data)
    profitability_data = extract_profitability_data(raw_data)
    funding_data = extract_funding_data(raw_data)
    employee_data = extract_employee_data(raw_data)
    ai_data = extract_ai_data(raw_data)
    scorecard_data = extract_scorecard_data(raw_data)

    # Determine derived values
    saas_score = scorecard_data["dimensions"].get("SaaS Maturity", {}).get("score", 5)
    ai_maturity = determine_ai_maturity(
        raw_data.get("ai_maturity", ""),
        ai_data["ai_score"],
        ai_data["ai_signal_level"],
        ai_data["ai_capabilities"],
        ai_data["ai_in_production"],
        saas_score,
    )
    threat_level = determine_threat_level(scorecard_data["composite_score"])

    # Normalize financials and build financial metric
    normalized_financials = _normalize_and_validate_financials(
        company_name, revenue_data, profitability_data, funding_data, employee_data
    )
    financial = _build_financial_metric(normalized_financials, revenue_data, profitability_data, employee_data)

    # EPIC-059: Validate financial conversion didn't lose critical fields
    if not _validate_financial_conversion(financial, raw_data):
        logger.warning(
            f"[EPIC-059] Financial conversion loss detected for {company_name} — proceeding with available data"
        )

    # Determine tier and derive AI score
    tier = determine_tier(normalized_financials["revenue"])
    ai_score = _derive_ai_score(ai_data, ai_maturity, raw_data)

    # Build metadata
    confidence_scores = _apply_signal_confidence_aliases(build_confidence_scores(raw_data))
    metric_sources = build_metric_sources(raw_data)
    source_links = convert_source_links(raw_data)
    enrichment_quality_metrics = build_enrichment_quality_metrics(raw_data)
    data_quality_tier = determine_data_quality_tier(raw_data)

    # EPIC-058: Directly build Company object instead of calling non-existent build_company_entity()
    # STORY-178: Populate top-level funding fields from funding_data (raw EUR, not normalized millions)
    company = Company(
        id=f"{company_name.lower().replace(' ', '-')}-{index}",
        name=company_name,
        industry=raw_data.get("industry", "Energy Software"),
        description=raw_data.get("description"),
        website=raw_data.get("website"),
        headquarters=raw_data.get("country") or estimate_headquarters(folder),
        founded_year=raw_data.get("founded_year"),
        tier=tier,
        threat_level=threat_level,
        ai_maturity=ai_maturity,
        saas_maturity=saas_score,
        tech_stack=raw_data.get("tech_stack", []),
        signal_confidences=confidence_scores,
        revenue_cagr_3yr=revenue_data.get("cagr_3yr"),
        revenue_cagr_5yr=revenue_data.get("cagr_5yr"),
        financials=financial,
        geographic_presence=extract_geographic_presence(raw_data),
        key_customers=[],
        enrichment_source_count=raw_data.get("enrichment_source_count", 0),
        enrichment_quality_metrics=enrichment_quality_metrics,
        data_quality_tier=data_quality_tier,
        data_source="Solstein Competitive Intelligence",
        last_updated=datetime.now(timezone.utc),
        data_source_type=raw_data.get(
            "data_source_type",
            "synthetic" if raw_data.get("is_synthetic", False) else "real",
        ),
        ai_score=ai_score,
        metric_sources=metric_sources,
        source_links=source_links,
        # STORY-178: top-level funding fields (raw EUR, not normalized to millions)
        total_funding_raised_eur=funding_data.get("total_funding_eur"),
        latest_valuation_eur=funding_data.get("latest_valuation_eur"),
        funding_rounds=funding_data.get("funding_rounds", []),
        lead_investors=funding_data.get("lead_investors", []),
        # STORY-179: top-level profitability fields (mirrors financials for direct access)
        ebitda_margin=profitability_data.get("ebitda_margin"),
        recurring_revenue_pct=profitability_data.get("recurring_revenue_pct"),
        revenue_per_employee_eur_k=profitability_data.get("revenue_per_employee_eur_k"),
        # STORY-178: top-level funding fields (raw EUR, not normalized to millions)
        total_funding_raised_eur=funding_data.get("total_funding_eur"),
        latest_valuation_eur=funding_data.get("latest_valuation_eur"),
        funding_rounds=funding_data.get("funding_rounds", []),
        lead_investors=funding_data.get("lead_investors", []),
    )
    return populate_signal_confidences(company)
