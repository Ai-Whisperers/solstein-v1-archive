"""Company data conversion utilities.

EPIC-021: Extracted from loaders.py as part of file splitting.
EPIC-020: Refactored convert_to_domain_company from 432 lines to <100 lines.

Converts raw JSON data to Company domain entities.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from solstein.core.scoring_utils import populate_signal_confidences
from solstein.domain.models import (
    AIMaturity,
    Company,
    CompanyTier,
    ConfidenceLevel,
    FinancialMetric,
    ThreatLevel,
)
from solstein.data.metric_contract import normalize_financial_payload

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


def estimate_headquarters(folder: str) -> str | None:
    """Estimate headquarters based on folder name."""
    folder_lower = folder.lower()

    if "uk" in folder_lower or "british" in folder_lower:
        return "United Kingdom"
    elif "german" in folder_lower or "deutsch" in folder_lower:
        return "Germany"
    elif "french" in folder_lower or "france" in folder_lower:
        return "France"
    elif "norway" in folder_lower or "norwegian" in folder_lower:
        return "Norway"
    elif "spain" in folder_lower or "spanish" in folder_lower:
        return "Spain"
    elif "poland" in folder_lower or "polish" in folder_lower:
        return "Poland"
    elif "swiss" in folder_lower or "switzerland" in folder_lower:
        return "Switzerland"
    else:
        return "Europe"


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


def convert_to_domain_company(raw_data: dict[str, Any], index: int) -> Company:
    """Convert raw JSON data to Company domain entity.

    EPIC-020: Refactored from 432-line monolithic function.
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

    # Normalize financials
    normalized_financials = normalize_financial_payload(
        {
            "revenue": revenue_data["latest_revenue"],
            "growth_rate": revenue_data["latest_growth"],
            "profit_margin": profitability_data["profit_margin"],
            "funding_raised": funding_data["total_funding_eur"],
            "valuation": funding_data["latest_valuation_eur"],
        }
    )

    # Build financial metric
    financial = FinancialMetric(
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

    # Determine tier
    tier = determine_tier(normalized_financials["revenue"])

    # Derive AI score if missing
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
        ai_score = ai_score_by_maturity.get(ai_maturity, 1.0)

    # Build metadata
    confidence_scores = build_confidence_scores(raw_data)
    metric_sources = build_metric_sources(raw_data)
    source_links = convert_source_links(raw_data)
    enrichment_quality_metrics = build_enrichment_quality_metrics(raw_data)
    data_quality_tier = determine_data_quality_tier(raw_data)
    # Create company using builder
    return build_company_entity(
        raw_data=raw_data,
        folder=folder,
        company_name=company_name,
        revenue_data=revenue_data,
        profitability_data=profitability_data,
        funding_data=funding_data,
        employee_data=employee_data,
        ai_data=ai_data,
        scorecard_data=scorecard_data,
        normalized_financials=normalized_financials,
        financial=financial,
        tier=tier,
        threat_level=threat_level,
        ai_maturity=ai_maturity,
        saas_score=saas_score,
        ai_score=ai_score,
        confidence_scores=confidence_scores,
        metric_sources=metric_sources,
        source_links=source_links,
        enrichment_quality_metrics=enrichment_quality_metrics,
        data_quality_tier=data_quality_tier,
    )
