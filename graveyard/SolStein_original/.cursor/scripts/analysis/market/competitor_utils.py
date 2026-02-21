#!/usr/bin/env python3
"""Shared utilities for competitor analysis scripts.

Provides common accessor functions and constants used across the market
analysis pipeline (extraction, markdown dashboard, Excel report).

Requirements:
    Python 3.10+
"""

import logging
import re
import time
from contextlib import contextmanager
from typing import Optional


@contextmanager
def timed_phase(name: str, *, profile: bool = False):
    """Context manager that measures and logs phase duration when profiling is enabled."""
    if not profile:
        yield
        return
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    logging.info("PROFILE: %s took %.3f seconds", name, elapsed)

CLASSIFICATION_ORDER = ["Rocket", "Riser", "Steady", "Dinosaur"]


def get_score(competitor: dict, dimension: str) -> Optional[float]:
    """Get a scorecard dimension score for a competitor."""
    return (
        competitor.get("scorecard", {})
        .get("dimensions", {})
        .get(dimension, {})
        .get("score")
    )


def get_composite(competitor: dict) -> Optional[float]:
    """Get composite score."""
    return competitor.get("scorecard", {}).get("composite_score")


def get_classification(competitor: dict) -> Optional[str]:
    """Get classification."""
    return competitor.get("scorecard", {}).get("classification")


def is_eneve(competitor: dict) -> bool:
    """Check if this competitor entry is Eneve."""
    return "eneve" in competitor.get("folder", "").lower()


# --- Profitability accessors ---


def get_ebitda_margin(competitor: dict) -> Optional[float]:
    """Get the latest EBITDA margin percentage."""
    return competitor.get("profitability", {}).get("ebitda_margin_pct")


def get_revenue_per_employee(competitor: dict) -> Optional[float]:
    """Get revenue per employee (EUR K)."""
    return competitor.get("profitability", {}).get("revenue_per_employee_eur_k")


# --- Funding accessors ---


def get_lead_investors(competitor: dict) -> list[str]:
    """Get deduplicated list of lead investors across all funding rounds."""
    return competitor.get("funding", {}).get("lead_investors", [])


def get_war_chest_signals(competitor: dict) -> Optional[str]:
    """Get war chest signals narrative text."""
    return competitor.get("funding", {}).get("war_chest_signals")


# --- Geographic accessors ---


def get_international_revenue_pct(competitor: dict) -> Optional[float]:
    """Get international revenue percentage."""
    return competitor.get("geographic", {}).get("international_revenue_pct")


def get_countries_count(competitor: dict) -> Optional[int]:
    """Get count of countries the competitor operates in."""
    return competitor.get("geographic", {}).get("countries_count")


# --- SaaS accessors ---


def get_deployment_model(competitor: dict) -> Optional[str]:
    """Get deployment model classification: 'SaaS', 'Hybrid', or 'On-Premise'."""
    return competitor.get("saas", {}).get("deployment_model")


def get_cloud_revenue_pct(competitor: dict) -> Optional[float]:
    """Get cloud revenue percentage."""
    return competitor.get("saas", {}).get("cloud_revenue_pct")


# --- AI Maturity accessors ---


def get_ai_score(competitor: dict) -> Optional[int]:
    """Get AI maturity score (0-10)."""
    return competitor.get("ai", {}).get("ai_score")


def get_ai_signal_level(competitor: dict) -> Optional[str]:
    """Get AI signal level: 'None', 'Low', 'Moderate', 'Strong', or 'Very Strong'."""
    return competitor.get("ai", {}).get("signal_level")


def get_ai_capabilities(competitor: dict) -> Optional[str]:
    """Get key AI capabilities description."""
    return competitor.get("ai", {}).get("key_capabilities")


def get_ai_staff_pct(competitor: dict) -> Optional[float]:
    """Get AI/ML staff percentage of total workforce."""
    return competitor.get("ai", {}).get("ai_staff_pct")


def get_ai_in_production(competitor: dict) -> bool:
    """Get whether AI features are deployed in production."""
    return competitor.get("ai", {}).get("in_production", False)


# --- AI Talent accessors ---


def get_ai_talent_team_size(competitor: dict) -> Optional[float]:
    """Get estimated AI/ML team headcount from ai-talent.md data."""
    return competitor.get("ai_talent", {}).get("team_size")


def get_ai_talent_pct_engineering(competitor: dict) -> Optional[float]:
    """Get AI team as % of engineering headcount."""
    return competitor.get("ai_talent", {}).get("ai_team_pct_engineering")


def get_ai_talent_pct_total(competitor: dict) -> Optional[float]:
    """Get AI team as % of total company headcount."""
    return competitor.get("ai_talent", {}).get("ai_team_pct_total")


def get_concentration_risk(competitor: dict) -> Optional[float]:
    """Get Talent Concentration Risk score (1-10, higher = more fragile)."""
    return competitor.get("ai_talent", {}).get("concentration_risk")


def get_acquihire_score(competitor: dict) -> Optional[float]:
    """Get Acqui-Hire Attractiveness score (1-10, higher = better target)."""
    return competitor.get("ai_talent", {}).get("acquihire_score")


def get_talent_flow(competitor: dict) -> Optional[str]:
    """Get net talent flow direction: Gaining / Losing / Stable."""
    return competitor.get("ai_talent", {}).get("net_talent_flow")


def get_ai_leadership_count(competitor: dict) -> int:
    """Get count of identified AI/ML leaders."""
    return len(competitor.get("ai_talent", {}).get("leadership", []))


def get_key_hires_count(competitor: dict) -> int:
    """Get count of key AI/ML hires in last 24 months."""
    return len(competitor.get("ai_talent", {}).get("key_hires", []))


def has_ai_talent_data(competitor: dict) -> bool:
    """Check if competitor has ai-talent.md data available."""
    talent = competitor.get("ai_talent", {})
    return bool(talent) and talent.get("data_available", False)


# --- Investment Efficiency calculators ---


def parse_total_raised_eur_m(text: Optional[str]) -> Optional[float]:
    """Best-effort extraction of total raised in EUR millions from free-form text.

    Returns None when the amount cannot be determined (undisclosed, N/A,
    complex multi-currency expressions, or bootstrapped companies).
    """
    if not text:
        return None

    lower = text.lower().strip()

    skip_markers = ("n/a", "not applicable", "undisclosed", "no external", "self-funded",
                    "bootstrapped", "unfunded", "no disclosed", "internally funded",
                    "publicly listed", "publicly traded", "public company")
    if any(m in lower for m in skip_markers):
        return None

    if re.fullmatch(r"eur\s*0.*", lower) or lower.startswith("€0") or lower == "0":
        return 0.0

    eur_billion = re.search(r"[~≈]?\s*EUR\s*([0-9]+(?:\.[0-9]+)?)\s*B", text, re.IGNORECASE)
    if eur_billion:
        return float(eur_billion.group(1)) * 1000

    eur_million = re.search(r"[~≈]?\s*EUR\s*([0-9]+(?:\.[0-9]+)?)\s*M", text, re.IGNORECASE)
    if eur_million:
        return float(eur_million.group(1))

    eur_paren = re.search(r"\(\s*[~≈]?\s*EUR\s*[~≈]?\s*([0-9]+(?:\.[0-9]+)?)\s*M\s*\)", text, re.IGNORECASE)
    if eur_paren:
        return float(eur_paren.group(1))

    eur_total = re.search(r"[~≈]?\s*EUR\s*([0-9]+(?:\.[0-9]+)?)\s*M\s*total", text, re.IGNORECASE)
    if eur_total:
        return float(eur_total.group(1))

    usd_billion = re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)\s*B", text)
    if usd_billion:
        return float(usd_billion.group(1)) * 1000 * 0.95

    usd_million = re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)\s*M", text)
    if usd_million:
        return float(usd_million.group(1)) * 0.95

    gbp_million = re.search(r"GBP\s*([0-9]+(?:\.[0-9]+)?)\s*M", text, re.IGNORECASE)
    if gbp_million:
        return float(gbp_million.group(1)) * 1.17

    return None


def calc_rev_per_employee_eur_k(comp: dict) -> Optional[float]:
    """Revenue per employee in EUR thousands."""
    rev_m = comp.get("revenue", {}).get("latest_revenue_eur_m")
    headcount = comp.get("employees", {}).get("latest_headcount")
    if not rev_m or not headcount or headcount == 0:
        return None
    return round(rev_m * 1000 / headcount, 0)


def calc_rev_per_eur_m_raised(comp: dict) -> Optional[float]:
    """Revenue generated per EUR million of external capital raised."""
    rev_m = comp.get("revenue", {}).get("latest_revenue_eur_m")
    raised = parse_total_raised_eur_m(comp.get("funding", {}).get("total_raised_text"))
    if not rev_m or raised is None or raised <= 0:
        return None
    return round(rev_m / raised, 2)


def calc_hiring_efficiency(comp: dict) -> Optional[float]:
    """Ratio of employee CAGR to revenue CAGR (lower = leaner growth)."""
    emp_cagr = comp.get("employees", {}).get("employee_cagr_pct")
    rev_cagr = comp.get("revenue", {}).get("cagr_3yr_pct")
    if not emp_cagr or not rev_cagr or rev_cagr == 0:
        return None
    return round(emp_cagr / rev_cagr, 2)


def calc_growth_roi(comp: dict) -> Optional[float]:
    """Composite score per EUR million raised -- growth return on capital."""
    composite = get_composite(comp)
    raised = parse_total_raised_eur_m(comp.get("funding", {}).get("total_raised_text"))
    if composite is None or raised is None or raised <= 0:
        return None
    return round(composite / raised * 100, 2)


__all__ = [
    "CLASSIFICATION_ORDER",
    "timed_phase",
    "get_score",
    "get_composite",
    "get_classification",
    "is_eneve",
    "get_ebitda_margin",
    "get_revenue_per_employee",
    "get_lead_investors",
    "get_war_chest_signals",
    "get_international_revenue_pct",
    "get_countries_count",
    "get_deployment_model",
    "get_cloud_revenue_pct",
    "get_ai_score",
    "get_ai_signal_level",
    "get_ai_capabilities",
    "get_ai_staff_pct",
    "get_ai_in_production",
    "parse_total_raised_eur_m",
    "calc_rev_per_employee_eur_k",
    "calc_rev_per_eur_m_raised",
    "calc_hiring_efficiency",
    "calc_growth_roi",
]
