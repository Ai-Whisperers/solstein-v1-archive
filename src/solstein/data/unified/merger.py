"""Data merging logic for unified company loader.

Extracted from unified_loader.py as part of EPIC-021 file splitting.
Handles merging JSON and Markdown data sources with conflict resolution.
"""

from __future__ import annotations

from datetime import datetime, timezone

from loguru import logger

from solstein.domain.models import Company, FinancialMetric

from .company import UnifiedCompany


def merge_companies(json_company: Company, markdown_company: Company) -> UnifiedCompany:
    """
    Merge JSON and Markdown companies with conflict resolution.
    Priority: Markdown > JSON
    """
    conflicts = []
    data_sources = {}

    # Start with JSON company as base
    merged = UnifiedCompany(**json_company.model_dump())

    # Merge financial metrics
    if json_company.financials and markdown_company.financials:
        merged_financials = merge_financials(
            json_company.financials, markdown_company.financials, conflicts, data_sources
        )
        merged.financials = merged_financials
    elif markdown_company.financials:
        merged.financials = markdown_company.financials
        data_sources["financials"] = "Markdown"

    # Merge other fields with Markdown priority
    if markdown_company.tier != json_company.tier:
        conflicts.append("tier")
        merged.tier = markdown_company.tier
        data_sources["tier"] = "Markdown"
    else:
        data_sources["tier"] = "JSON"

    if markdown_company.ai_maturity != json_company.ai_maturity:
        conflicts.append("ai_maturity")
        merged.ai_maturity = markdown_company.ai_maturity
        data_sources["ai_maturity"] = "Markdown"
        # Infer AI score from AI maturity when there's a conflict
        infer_ai_score_from_maturity(merged, markdown_company.ai_maturity)
    else:
        data_sources["ai_maturity"] = "JSON"
        # Also check if AI score is 0 but maturity is Strong/Very Strong - fix contradiction
        if merged.ai_score == 0 and merged.ai_maturity in ["Strong", "Very Strong"]:
            infer_ai_score_from_maturity(merged, merged.ai_maturity)

    if markdown_company.threat_level != json_company.threat_level:
        conflicts.append("threat_level")
        merged.threat_level = markdown_company.threat_level
        data_sources["threat_level"] = "Markdown"
    else:
        data_sources["threat_level"] = "JSON"

    if markdown_company.geographic_presence != json_company.geographic_presence:
        conflicts.append("geographic_presence")
        merged.geographic_presence = markdown_company.geographic_presence
        data_sources["geographic_presence"] = "Markdown"
    else:
        data_sources["geographic_presence"] = "JSON"

    # Set tracking fields
    merged.data_source_per_field = data_sources
    merged.merge_conflicts = conflicts
    merged.merge_timestamp = datetime.now(timezone.utc)

    if conflicts:
        logger.info(f"Merged {merged.name} with {len(conflicts)} conflicts: {conflicts}")

    return merged


def merge_financials(
    json_fin: FinancialMetric,
    markdown_fin: FinancialMetric,
    conflicts: list[str],
    data_sources: dict[str, str],
) -> FinancialMetric:
    """Merge financial metrics with Markdown priority."""
    # Start with JSON
    merged = FinancialMetric(**json_fin.model_dump(), allow_empty_primary=True)

    # Apply Markdown values with priority
    if markdown_fin.revenue is not None and markdown_fin.revenue != json_fin.revenue:
        conflicts.append("revenue")
        merged.revenue = markdown_fin.revenue
        merged.revenue_confidence = markdown_fin.revenue_confidence
        data_sources["revenue"] = "Markdown"
    else:
        data_sources["revenue"] = "JSON"

    if markdown_fin.growth_rate is not None and markdown_fin.growth_rate != json_fin.growth_rate:
        conflicts.append("growth_rate")
        merged.growth_rate = markdown_fin.growth_rate
        merged.growth_confidence = markdown_fin.growth_confidence
        data_sources["growth_rate"] = "Markdown"
    else:
        data_sources["growth_rate"] = "JSON"

    if markdown_fin.employees is not None and markdown_fin.employees != json_fin.employees:
        conflicts.append("employees")
        merged.employees = markdown_fin.employees
        merged.employees_confidence = markdown_fin.employees_confidence
        data_sources["employees"] = "Markdown"
    else:
        data_sources["employees"] = "JSON"

    if markdown_fin.profit_margin is not None and markdown_fin.profit_margin != json_fin.profit_margin:
        conflicts.append("profit_margin")
        merged.profit_margin = markdown_fin.profit_margin
        merged.margin_confidence = markdown_fin.margin_confidence
        data_sources["profit_margin"] = "Markdown"
    else:
        data_sources["profit_margin"] = "JSON"

    if markdown_fin.funding_raised is not None and markdown_fin.funding_raised != json_fin.funding_raised:
        conflicts.append("funding_raised")
        merged.funding_raised = markdown_fin.funding_raised
        merged.funding_confidence = markdown_fin.funding_confidence
        data_sources["funding_raised"] = "Markdown"
    else:
        data_sources["funding_raised"] = "JSON"

    if markdown_fin.valuation is not None and markdown_fin.valuation != json_fin.valuation:
        conflicts.append("valuation")
        merged.valuation = markdown_fin.valuation
        merged.valuation_confidence = markdown_fin.valuation_confidence
        data_sources["valuation"] = "Markdown"
    else:
        data_sources["valuation"] = "JSON"

    return merged


def convert_to_unified(company: Company, source: str) -> UnifiedCompany:
    """Convert a Company to UnifiedCompany with source tracking."""
    data = company.model_dump()
    if data.get("financials") is not None:
        data["financials"]["allow_empty_primary"] = True
    unified = UnifiedCompany(**data)

    # Track all fields as coming from single source
    unified.data_source_per_field = {
        "revenue": source,
        "growth_rate": source,
        "employees": source,
        "profit_margin": source,
        "funding_raised": source,
        "valuation": source,
        "tier": source,
        "ai_maturity": source,
        "threat_level": source,
        "geographic_presence": source,
    }
    unified.merge_conflicts = []
    unified.merge_timestamp = datetime.now(timezone.utc)

    return unified


def infer_ai_score_from_maturity(company: UnifiedCompany, ai_maturity: str) -> None:
    """Infer AI score from AI maturity level when there's a conflict.

    Maps AI maturity levels to scores using the CompetitivePositionConfig mapping.
    This fixes contradictions like 'Strong' maturity with 0/10 score.
    """
    from solstein.core.scoring_config import CompetitivePositionConfig

    config = CompetitivePositionConfig()
    ai_maturity_scores = config.ai_maturity_scores

    # Map AI maturity to score (0-10 scale)
    # CompetitivePositionConfig uses -1.0 to 2.5 scale, so we need to normalize to 0-10
    maturity_score = ai_maturity_scores.get(ai_maturity, 0.0)
    # Normalize: -1.0 to 2.5 range maps to 0-10 range
    # Formula: ((maturity_score - (-1.0)) / (2.5 - (-1.0))) * 10
    normalized_score = ((maturity_score - (-1.0)) / (2.5 - (-1.0))) * 10
    normalized_score = max(0, min(10, int(round(normalized_score))))  # Round to int and clamp to 0-10

    company.ai_score = normalized_score
    logger.info(f"Inferred AI score {normalized_score}/10 for {company.name} from AI maturity '{ai_maturity}'")
