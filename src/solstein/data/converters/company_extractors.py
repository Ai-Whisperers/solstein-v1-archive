"""Company data extraction helpers.

EPIC-020: Extracted from convert_to_domain_company function.
Each extractor handles one domain of data extraction.
"""

from __future__ import annotations

import re
from typing import Any

from loguru import logger

from solstein.data.parsers.confidence import convert_confidence
from solstein.domain.models import AIMaturity, ConfidenceLevel, ThreatLevel


def extract_revenue_data(raw_data: dict[str, Any]) -> dict[str, Any]:
    """Extract revenue data from raw JSON.

    EPIC-058: Supports both flat (float at top level) and nested (dict with timeline) formats.
    Auto-detects format and extracts with no field loss.
    """
    revenue_data = raw_data.get("revenue", {})
    growth_rate_data = raw_data.get("growth_rate")

    timeline = []
    latest_revenue = None
    latest_growth = None
    revenue_confidence = ConfidenceLevel.UNKNOWN
    cagr_3yr = None
    cagr_5yr = None
    detected_format = None

    if isinstance(revenue_data, dict) and revenue_data:
        detected_format = "nested"
        timeline = revenue_data.get("timeline", [])
        cagr_3yr = revenue_data.get("cagr_3yr_pct")
        cagr_5yr = revenue_data.get("cagr_5yr_pct")

        if timeline and len(timeline) > 0:
            latest = timeline[0]
            latest_revenue = latest.get("eur_millions")
            latest_growth = latest.get("yoy_growth_pct")
            revenue_confidence = convert_confidence(latest.get("confidence"))
            logger.debug(f"[EPIC-058] Detected nested format: revenue={latest_revenue}, growth={latest_growth}")

    if latest_revenue is None and isinstance(revenue_data, (int, float)):
        detected_format = "flat"
        latest_revenue = float(revenue_data)
        revenue_confidence = ConfidenceLevel.CONFIRMED
        logger.debug(f"[EPIC-058] Detected flat format: revenue={latest_revenue}")

    if latest_growth is None and isinstance(growth_rate_data, (int, float)):
        latest_growth = float(growth_rate_data)
        logger.debug(f"[EPIC-058] Extracted growth_rate from flat field: {latest_growth}")

    if cagr_3yr is None:
        cagr_3yr = raw_data.get("revenue_cagr_3yr")
    if cagr_5yr is None:
        cagr_5yr = raw_data.get("revenue_cagr_5yr")

    calculated_cagr_3yr = cagr_3yr
    if not calculated_cagr_3yr and timeline and len(timeline) >= 2:
        try:
            years_back = min(3, len(timeline))
            if years_back >= 2:
                current_rev = timeline[0].get("eur_millions", 0)
                past_rev = timeline[years_back - 1].get("eur_millions", 0)
                if current_rev and past_rev and past_rev > 0:
                    calculated_cagr_3yr = ((current_rev / past_rev) ** (1 / years_back) - 1) * 100
        except (ZeroDivisionError, ValueError) as e:
            logger.debug(f"Could not calculate 3-year CAGR: {e}")

    return {
        "timeline": timeline,
        "latest_revenue": latest_revenue,
        "latest_growth": latest_growth,
        "revenue_confidence": revenue_confidence,
        "cagr_3yr": calculated_cagr_3yr if calculated_cagr_3yr else cagr_3yr,
        "cagr_5yr": cagr_5yr,
        "detected_format": detected_format,
    }


def extract_profitability_data(raw_data: dict[str, Any]) -> dict[str, Any]:
    """Extract profitability data from raw JSON.

    EPIC-058: Supports both flat and nested formats.
    """
    profitability_data = raw_data.get("profitability", {})

    ebitda_margin = None
    recurring_rev_pct = None
    rev_per_employee = None
    raw_metrics = {}
    detected_format = None

    if isinstance(profitability_data, dict) and profitability_data:
        detected_format = "nested"
        ebitda_margin = profitability_data.get("ebitda_margin_pct")
        recurring_rev_pct = profitability_data.get("recurring_revenue_pct")
        rev_per_employee = profitability_data.get("revenue_per_employee_eur_k")
        raw_metrics = profitability_data.get("raw_metrics", {})
        if ebitda_margin:
            logger.debug(f"[EPIC-058] Detected nested profitability: ebitda={ebitda_margin}%")

    if ebitda_margin is None and isinstance(raw_data.get("ebitda_margin_pct"), (int, float)):
        detected_format = "flat"
        ebitda_margin = float(raw_data.get("ebitda_margin_pct"))
        logger.debug(f"[EPIC-058] Detected flat profitability: ebitda={ebitda_margin}%")

    if recurring_rev_pct is None and isinstance(raw_data.get("recurring_revenue_pct"), (int, float)):
        recurring_rev_pct = float(raw_data.get("recurring_revenue_pct"))
        logger.debug(f"[EPIC-058] Extracted flat recurring_revenue_pct: {recurring_rev_pct}%")

    profit_margin = _extract_profit_margin(raw_metrics, raw_data)

    return {
        "ebitda_margin": ebitda_margin,
        "recurring_revenue_pct": recurring_rev_pct,
        "revenue_per_employee_eur_k": rev_per_employee,
        "profit_margin": profit_margin,
        "raw_metrics": raw_metrics,
        "detected_format": detected_format,
    }


def _extract_profit_margin(raw_metrics: dict, raw_data: dict[str, Any]) -> float | None:
    """Extract profit margin using multiple strategies."""
    # Strategy 1: Direct numeric value
    if raw_metrics:
        for key, value in raw_metrics.items():
            if "margin" in key.lower() and isinstance(value, (int, float)):
                return float(value)

    # Strategy 2: Parse string like "0.7% margin" or "33.7%"
    if raw_metrics:
        for key, value in raw_metrics.items():
            if "margin" in key.lower() and isinstance(value, str):
                match = re.search(r"([\d.]+)\s*%", value)
                if match:
                    return float(match.group(1))
                match = re.search(r"([\d.]+)", value)
                if match:
                    val = float(match.group(1))
                    if val <= 100:
                        return val

    # Strategy 3: Calculate from net profit and revenue
    if raw_metrics:
        profit_margin = _calculate_profit_margin_from_metrics(raw_metrics)
        if profit_margin:
            return profit_margin

    # Strategy 4: Check root-level profit_margin
    root_pm = raw_data.get("profit_margin")
    if isinstance(root_pm, (int, float)):
        return root_pm * 100 if root_pm < 1 else root_pm

    return None


def _calculate_profit_margin_from_metrics(raw_metrics: dict) -> float | None:
    """Calculate profit margin from net profit and revenue."""
    net_profit = None
    net_revenue_key = None

    for key in raw_metrics.keys():
        if "net profit" in key.lower() and "(fy" in key.lower():
            net_profit = raw_metrics[key]
            for rev_key in raw_metrics.keys():
                if "revenue" in rev_key.lower() or "sales" in rev_key.lower():
                    net_revenue_key = rev_key
                    break
            break

    if not (net_profit and net_revenue_key):
        return None

    try:
        # Parse net profit with currency conversion
        np_match = re.search(r"([\d.]+)", str(net_profit))
        if not np_match:
            return None

        np_val = float(np_match.group(1))
        np_str = str(net_profit).lower()
        if "dkk" in np_str:
            np_val *= 0.134
        elif "gbp" in np_str:
            np_val *= 1.18

        # Parse revenue with currency conversion
        rev_match = re.search(r"([\d.]+)", str(raw_metrics[net_revenue_key]))
        if not rev_match:
            return None

        rev_val = float(rev_match.group(1))
        rev_str = str(raw_metrics[net_revenue_key]).lower()
        if "dkk" in rev_str:
            rev_val *= 0.134
        elif "gbp" in rev_str:
            rev_val *= 1.18

        if rev_val > 0:
            return (np_val / rev_val) * 100

    except (ValueError, TypeError, KeyError, ZeroDivisionError) as e:
        logger.debug(f"Could not parse profit margin: {e}")

    return None


def extract_funding_data(raw_data: dict[str, Any]) -> dict[str, Any]:
    """Extract funding data from raw JSON."""
    from solstein.data.parsers.funding import parse_funding_amount, parse_valuation

    funding_data = raw_data.get("funding", {})

    if isinstance(funding_data, dict) and funding_data:
        # Original nested format
        return {
            "funding_rounds": funding_data.get("rounds", []),
            "total_raised_text": funding_data.get("total_raised_text", ""),
            "latest_valuation_text": funding_data.get("latest_valuation_text", ""),
            "lead_investors": funding_data.get("lead_investors", []),
            "war_chest_signals": funding_data.get("war_chest_signals"),
            "total_funding_eur": parse_funding_amount(funding_data.get("total_raised_text", "")),
            "latest_valuation_eur": parse_valuation(funding_data.get("latest_valuation_text", "")),
        }
    else:
        # Flat format
        return {
            "funding_rounds": raw_data.get("funding_rounds", []),
            "lead_investors": raw_data.get("lead_investors", []),
            "war_chest_signals": raw_data.get("war_chest_signals"),
            "total_funding_eur": raw_data.get("funding_raised"),
            "latest_valuation_eur": raw_data.get("valuation"),
            "total_raised_text": "",
            "latest_valuation_text": "",
        }


def extract_employee_data(raw_data: dict[str, Any]) -> dict[str, Any]:
    """Extract employee data from raw JSON."""
    employees_data = raw_data.get("employees", {})

    if isinstance(employees_data, (int, float)):
        # Ivan's simplified format
        return {
            "employee_count": int(employees_data),
            "employee_cagr": raw_data.get("employee_cagr_pct"),
            "open_positions": raw_data.get("open_positions"),
        }
    elif isinstance(employees_data, dict):
        # Original nested format
        count_raw = employees_data.get("latest_headcount")
        return {
            "employee_count": int(count_raw) if count_raw else None,
            "employee_cagr": employees_data.get("employee_cagr_pct"),
            "open_positions": employees_data.get("open_positions"),
        }
    else:
        return {
            "employee_count": None,
            "employee_cagr": None,
            "open_positions": None,
        }


def extract_ai_data(raw_data: dict[str, Any]) -> dict[str, Any]:
    """Extract AI capabilities data from raw JSON."""
    ai_data = raw_data.get("ai", {})

    if isinstance(ai_data, dict) and ai_data:
        # Original nested format
        return {
            "ai_score": ai_data.get("ai_score"),
            "ai_signal_level": ai_data.get("signal_level"),
            "ai_capabilities": ai_data.get("key_capabilities"),
            "ai_in_production": ai_data.get("in_production"),
        }
    else:
        # Flat format
        return {
            "ai_score": raw_data.get("ai_score") or raw_data.get("ai_maturity_score"),
            "ai_signal_level": raw_data.get("ai_signal_level"),
            "ai_capabilities": raw_data.get("ai_key_capabilities"),
            "ai_in_production": raw_data.get("ai_in_production"),
        }


def extract_scorecard_data(raw_data: dict[str, Any]) -> dict[str, Any]:
    """Extract scorecard data from raw JSON."""
    scorecard = raw_data.get("scorecard", {})

    if isinstance(scorecard, dict) and scorecard:
        return {
            "dimensions": scorecard.get("dimensions", {}),
            "composite_score": scorecard.get("composite_score", 5),
            "classification": scorecard.get("classification"),
        }
    else:
        return {
            "dimensions": {},
            "composite_score": raw_data.get("composite_score", 5),
            "classification": raw_data.get("classification"),
        }


def determine_ai_maturity(
    ai_maturity_str: str,
    ai_score: float | None,
    ai_signal_level: str | None,
    ai_capabilities: list | None,
    ai_in_production: bool | None,
    saas_score: int,
) -> AIMaturity:
    """Determine AI maturity level from various signals."""
    any(
        [
            bool(ai_maturity_str),
            ai_signal_level is not None,
            bool(ai_capabilities),
            ai_in_production is not None,
        ]
    )

    if ai_maturity_str:
        # Map string values to enum
        ai_maturity_str = ai_maturity_str.strip().lower()
        if ai_maturity_str in ("strong", "advanced", "mature"):
            return AIMaturity.STRONG
        elif ai_maturity_str in ("moderate", "intermediate", "developing"):
            return AIMaturity.MODERATE
        else:
            return AIMaturity.LOW

    # Fall back to numeric scoring
    if ai_score is not None:
        if ai_score >= 8:
            return AIMaturity.STRONG
        elif ai_score >= 5:
            return AIMaturity.MODERATE
        else:
            return AIMaturity.LOW

    # Use SaaS score as fallback
    if saas_score >= 8:
        return AIMaturity.STRONG
    elif saas_score >= 5:
        return AIMaturity.MODERATE
    else:
        return AIMaturity.LOW


def determine_threat_level(composite_score: float) -> ThreatLevel:
    """Determine threat level from composite score."""
    if composite_score >= 8:
        return ThreatLevel.HIGH
    elif composite_score >= 6:
        return ThreatLevel.MEDIUM
    else:
        return ThreatLevel.LOW


def build_confidence_scores(raw_data: dict[str, Any]) -> dict[str, float]:
    """Build confidence scores dictionary from raw confidence fields."""
    confidence_level_map = {
        "confirmed": 1.0,
        "high": 0.9,
        "strong": 0.85,
        "medium": 0.6,
        "moderate": 0.5,
        "low": 0.3,
        "weak": 0.2,
        "estimated": 0.5,
        "unknown": 0.0,
    }

    def convert_confidence_value(value):
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            return confidence_level_map.get(value.lower(), 0.5)
        return 0.0

    def extract_revenue_confidences(revenue_data):
        """Extract confidence levels from revenue timeline entries."""
        confidences = {}
        if not isinstance(revenue_data, dict):
            return confidences
        timeline = revenue_data.get("timeline", [])
        for entry in timeline:
            if isinstance(entry, dict):
                year = entry.get("year")
                confidence = entry.get("confidence")
                if year and confidence:
                    confidences[f"revenue_{year}"] = convert_confidence_value(confidence)
        return confidences

    confidence_scores = {}

    # Add revenue timeline confidences
    revenue_confidences = extract_revenue_confidences(raw_data.get("revenue", {}))
    confidence_scores.update(revenue_confidences)

    # Add other confidence scores
    if raw_data.get("classification_confidence"):
        confidence_scores["classification"] = convert_confidence_value(raw_data["classification_confidence"])
    if raw_data.get("ai_confidence"):
        confidence_scores["ai_score"] = convert_confidence_value(raw_data["ai_confidence"])
    if raw_data.get("employees_confidence"):
        confidence_scores["employees"] = convert_confidence_value(raw_data["employees_confidence"])
    if raw_data.get("funding_confidence"):
        confidence_scores["funding"] = convert_confidence_value(raw_data["funding_confidence"])
    if raw_data.get("valuation_confidence"):
        confidence_scores["valuation"] = convert_confidence_value(raw_data["valuation_confidence"])
    if raw_data.get("valuation_confidence"):
        confidence_scores["valuation"] = convert_confidence_value(raw_data["valuation_confidence"])

    # EPIC-058: Extract confidence from metric_lineage if available
    metric_lineage = raw_data.get("metric_lineage", {})
    if isinstance(metric_lineage, dict):
        for field_name, metadata in metric_lineage.items():
            if isinstance(metadata, dict) and "confidence" in metadata:
                confidence_value = metadata.get("confidence")
                if isinstance(confidence_value, (int, float)):
                    confidence_scores[field_name] = float(confidence_value)
                    logger.debug(
                        f"[EPIC-058] Extracted {field_name} confidence from metric_lineage: {confidence_value}"
                    )

    return confidence_scores


def build_metric_sources(raw_data: dict[str, Any]) -> dict[str, list[str]]:
    """Build metric sources dictionary from raw source fields."""
    metric_sources = {}

    if raw_data.get("employees_source"):
        metric_sources["employees"] = [raw_data["employees_source"]]
    if raw_data.get("ai_source"):
        metric_sources["ai_score"] = [raw_data["ai_source"]]
    if raw_data.get("funding_source"):
        metric_sources["funding"] = [raw_data["funding_source"]]
    if raw_data.get("valuation_source"):
        metric_sources["valuation"] = [raw_data["valuation_source"]]

    # Add profitability source if available
    profitability_data = raw_data.get("profitability", {})
    if isinstance(profitability_data, dict) and profitability_data.get("source"):
        metric_sources["profitability"] = [profitability_data["source"]]

    return metric_sources


def convert_source_links(raw_data: dict[str, Any]) -> list[str]:
    """Convert source_links from objects to strings."""
    source_links = []
    raw_source_links = raw_data.get("source_links", [])

    for link in raw_source_links:
        if isinstance(link, dict) and link.get("source"):
            source_links.append(link["source"])
        elif isinstance(link, str):
            source_links.append(link)

    return source_links


def build_enrichment_quality_metrics(raw_data: dict[str, Any]) -> dict[str, Any]:
    """Build enrichment quality metrics dictionary."""
    metrics = {}

    if raw_data.get("data_quality_score") is not None:
        metrics["data_quality_score"] = raw_data["data_quality_score"]
    if raw_data.get("enrichment_source_count") is not None:
        metrics["source_count"] = raw_data["enrichment_source_count"]

    return metrics


def determine_data_quality_tier(raw_data: dict[str, Any]) -> str:
    """Determine data quality tier from quality score."""
    score = raw_data.get("data_quality_score", 0)
    if score >= 0.7:
        return "high"
    elif score >= 0.4:
        return "medium"
    else:
        return "low"
