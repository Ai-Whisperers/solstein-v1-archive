"""Red flag detection for PE due diligence (STORY-147).

Scans company signals for risk indicators that should be surfaced
during the due diligence process. Each detector function returns a
list of RedFlag objects.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .models import RedFlag, RedFlagSeverity

if TYPE_CHECKING:
    from solstein.domain.models import Company


# ---------------------------------------------------------------------------
# Legacy technology keywords
# ---------------------------------------------------------------------------

_LEGACY_KEYWORDS = frozenset(
    {
        "cobol",
        "mainframe",
        "on-premise",
        "on-prem",
        "legacy",
        "fortran",
        "delphi",
        "foxpro",
        "access",
        "vba",
    }
)

_NO_API_KEYWORDS = frozenset(
    {
        "no api",
        "no rest",
        "manual",
        "spreadsheet-driven",
    }
)


def detect_red_flags(company: Company) -> list[RedFlag]:
    """Run all red-flag detectors against a company and return findings."""
    flags: list[RedFlag] = []
    flags.extend(_check_technology(company))
    flags.extend(_check_data_maturity(company))
    flags.extend(_check_ai_readiness(company))
    flags.extend(_check_financial(company))
    flags.extend(_check_talent(company))
    return flags


# ---------------------------------------------------------------------------
# Individual detectors
# ---------------------------------------------------------------------------


def _check_technology(company: Company) -> list[RedFlag]:
    """Detect technology-related red flags."""
    flags: list[RedFlag] = []
    tech_stack = [s.lower() for s in getattr(company, "tech_stack", [])]

    legacy_items = [s for s in tech_stack if s in _LEGACY_KEYWORDS]
    if len(legacy_items) >= 2:
        flags.append(
            RedFlag(
                category="technology",
                title="Heavy legacy technology stack",
                description=(
                    f"Multiple legacy technologies detected: {', '.join(legacy_items)}. "
                    "This significantly increases AI transformation cost and risk."
                ),
                severity=RedFlagSeverity.CRITICAL,
                recommendation="Budget 40-60% premium for modernisation before AI adoption",
                evidence=f"Tech stack: {', '.join(tech_stack)}",
            )
        )
    elif len(legacy_items) == 1:
        flags.append(
            RedFlag(
                category="technology",
                title="Legacy technology component present",
                description=f"Legacy technology detected: {legacy_items[0]}",
                severity=RedFlagSeverity.MEDIUM,
                recommendation="Plan phased migration away from legacy component",
                evidence=f"Tech stack: {', '.join(tech_stack)}",
            )
        )

    if not tech_stack:
        flags.append(
            RedFlag(
                category="technology",
                title="No technology stack data available",
                description="Unable to assess technology risk — no stack information",
                severity=RedFlagSeverity.MEDIUM,
                recommendation="Request technology audit during DD data room review",
                evidence="tech_stack field is empty",
            )
        )

    return flags


def _check_data_maturity(company: Company) -> list[RedFlag]:
    """Detect data maturity red flags."""
    flags: list[RedFlag] = []
    saas_maturity = getattr(company, "saas_maturity", 1)

    if saas_maturity <= 2:
        flags.append(
            RedFlag(
                category="data",
                title="Very low data/SaaS maturity",
                description=(
                    f"SaaS maturity score: {saas_maturity}/10. "
                    "Company likely lacks structured data pipelines, "
                    "making AI adoption very difficult."
                ),
                severity=RedFlagSeverity.HIGH,
                recommendation="Require data platform investment as pre-condition",
                evidence=f"saas_maturity={saas_maturity}",
            )
        )
    elif saas_maturity <= 4:
        flags.append(
            RedFlag(
                category="data",
                title="Below-average data maturity",
                description=f"SaaS maturity score: {saas_maturity}/10",
                severity=RedFlagSeverity.MEDIUM,
                recommendation="Include data modernisation in 100-day plan",
                evidence=f"saas_maturity={saas_maturity}",
            )
        )

    return flags


def _check_ai_readiness(company: Company) -> list[RedFlag]:
    """Detect AI readiness red flags."""
    flags: list[RedFlag] = []

    ai_maturity = str(getattr(company, "ai_maturity", "None")).lower()
    ai_score = getattr(company, "ai_score", None)

    if ai_maturity in ("none", "low"):
        flags.append(
            RedFlag(
                category="ai_readiness",
                title="No meaningful AI capability",
                description=(
                    f"AI maturity: {ai_maturity}. Company has no AI initiatives, increasing transformation risk."
                ),
                severity=RedFlagSeverity.HIGH,
                recommendation="Factor 12-24 months AI capability build-up into plan",
                evidence=f"ai_maturity={ai_maturity}",
            )
        )

    if ai_score is not None and ai_score < 3.0:
        flags.append(
            RedFlag(
                category="ai_readiness",
                title="Very low AI score",
                description=f"AI score: {ai_score}/10 — bottom quartile",
                severity=RedFlagSeverity.HIGH,
                recommendation="Assess whether AI transformation is viable within target timeline",
                evidence=f"ai_score={ai_score}",
            )
        )

    return flags


def _check_financial(company: Company) -> list[RedFlag]:
    """Detect financial red flags relevant to AI transformation."""
    flags: list[RedFlag] = []

    revenue = company.revenue
    growth_rate = company.growth_rate

    if growth_rate is not None and growth_rate < 0:
        flags.append(
            RedFlag(
                category="financial",
                title="Negative revenue growth",
                description=(f"Growth rate: {growth_rate}%. Declining revenue may limit AI investment capacity."),
                severity=RedFlagSeverity.HIGH,
                recommendation="Stabilise revenue before committing to AI transformation budget",
                evidence=f"growth_rate={growth_rate}",
            )
        )

    if revenue is not None and revenue < 1_000_000:
        flags.append(
            RedFlag(
                category="financial",
                title="Very small revenue base",
                description=f"Revenue: EUR {revenue:,.0f} — may lack budget for AI investment",
                severity=RedFlagSeverity.MEDIUM,
                recommendation="Consider staged micro-investments or AI-as-a-Service approach",
                evidence=f"revenue={revenue}",
            )
        )

    return flags


def _check_talent(company: Company) -> list[RedFlag]:
    """Detect talent-related red flags."""
    flags: list[RedFlag] = []

    employees: int | None = None
    if company.financials is not None:
        employees = getattr(company.financials, "employees", None)

    if employees is not None and employees < 30:
        flags.append(
            RedFlag(
                category="talent",
                title="Very small team for AI transformation",
                description=(f"Employee count: {employees}. Team may lack capacity for parallel AI initiatives."),
                severity=RedFlagSeverity.HIGH,
                recommendation="Plan for outsourced AI team or acqui-hire strategy",
                evidence=f"employees={employees}",
            )
        )

    return flags
