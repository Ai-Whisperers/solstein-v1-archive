"""Helper functions for report generation.

Extracted from generator.py as part of EPIC-021 file splitting.
Contains utility functions for scoring, interpreting, and formatting report data.
"""

from __future__ import annotations

from solstein.domain.models import Company


def classify_trajectory(company: Company) -> str:
    """Classify company trajectory based on scores."""
    score = company.composite_score or 5
    if score >= 7:
        return "high-growth"
    elif score >= 5:
        return "steady"
    else:
        return "legacy"


def calculate_3yr_growth(company: Company) -> str:
    """Calculate 3-year revenue growth percentage."""
    if company.revenue_cagr_3yr:
        # CAGR formula: (1 + CAGR)^3 - 1
        growth = ((1 + company.revenue_cagr_3yr / 100) ** 3 - 1) * 100
        return f"{growth:.0f}%"
    return "N/A"


def generate_strengths(company: Company) -> str:
    """Generate strengths section."""
    strengths = []
    if company.financials.revenue and company.financials.revenue > 20:
        strengths.append(f"Revenue scale: €{company.financials.revenue:.1f}M")
    if company.revenue_cagr_3yr and company.revenue_cagr_3yr > 20:
        strengths.append(f"Strong growth: {company.revenue_cagr_3yr}% CAGR")
    if company.saas_maturity and company.saas_maturity >= 6:
        strengths.append(f"Advanced SaaS maturity: {company.saas_maturity}/10")
    if company.ai_score and company.ai_score >= 5:
        strengths.append(f"AI capabilities: {company.ai_score}/10")
    if company.geographic_presence and len(company.geographic_presence) > 2:
        strengths.append(f"Geographic expansion: {len(company.geographic_presence)} countries")

    return (
        "\n".join([f"{i + 1}. {s}" for i, s in enumerate(strengths)])
        if strengths
        else "No significant strengths identified"
    )


def generate_weaknesses(company: Company) -> str:
    """Generate weaknesses section."""
    weaknesses = []
    if company.ai_score is not None and company.ai_score < 3:
        weaknesses.append(f"Limited AI capabilities: {company.ai_score}/10")
    if company.saas_maturity and company.saas_maturity < 4:
        weaknesses.append(f"Low SaaS maturity: {company.saas_maturity}/10")
    if company.revenue_cagr_3yr and company.revenue_cagr_3yr < 5:
        weaknesses.append(f"Low organic growth: {company.revenue_cagr_3yr}% CAGR")
    if not company.latest_valuation_eur:
        weaknesses.append("No public valuation disclosed")

    return (
        "\n".join([f"{i + 1}. {w}" for i, w in enumerate(weaknesses)])
        if weaknesses
        else "No significant weaknesses identified"
    )


def generate_strategic_assessment(company: Company) -> str:
    """Generate strategic assessment."""
    score = company.composite_score or 5

    if score >= 7:
        return f"""> [!IMPORTANT]
> **{company.name}** is a high-growth company with strong market momentum.
> With a composite score of {score:.1f}, the company demonstrates excellence across
> growth, financial health, and competitive positioning. The 🔥 **Phoenix**
> classification indicates significant market disruption potential."""
    elif score >= 4:
        return f"""> [!NOTE]
> **{company.name}** shows solid fundamentals with room for improvement.
> At {score:.1f} composite score, the company demonstrates 🧂 **Salt**
> characteristics with steady growth. Key opportunities include AI adoption and
> international expansion."""
    else:
        return f"""> [!WARNING]
> **{company.name}** faces significant competitive challenges.
> With a composite score of {score:.1f}, the company ranks below market leaders.
> The ⚖️ **Lead** classification suggests legacy positioning
> that requires strategic transformation."""


def format_funding_rounds(funding_rounds: list) -> str:
    """Format funding rounds for display."""
    if not funding_rounds:
        return "No funding rounds recorded"

    lines = []
    for round_data in funding_rounds[:5]:
        date = round_data.get("date", "N/A")
        round_type = round_data.get("round", "Unknown")
        amount = round_data.get("amount", "Undisclosed")
        lines.append(f"- **{date}**: {round_type} - {amount}")

    return "\n".join(lines) if lines else "No funding rounds recorded"


def format_funding_detail(funding_rounds: list) -> str:
    """Format detailed funding information."""
    if not funding_rounds:
        return "**Funding Details**: No rounds disclosed"

    return "### Funding Rounds\n\n" + format_funding_rounds(funding_rounds)


def score_funding(company: Company) -> int:
    """Calculate funding score."""
    if company.total_funding_raised_eur and company.total_funding_raised_eur > 100e6:
        return 10
    elif company.total_funding_raised_eur and company.total_funding_raised_eur > 50e6:
        return 8
    elif company.total_funding_raised_eur and company.total_funding_raised_eur > 10e6:
        return 6
    elif company.funding_rounds:
        return 4
    else:
        return 2


def score_employee_growth(company: Company) -> int:
    """Calculate employee growth score."""
    cagr = company.employee_cagr_3yr
    if cagr and cagr > 30:
        return 10
    elif cagr and cagr > 20:
        return 7
    elif cagr and cagr > 10:
        return 5
    elif cagr and cagr > 0:
        return 3
    else:
        return 2


def score_geographic(company: Company) -> int:
    """Calculate geographic expansion score."""
    countries = len(company.geographic_presence) if company.geographic_presence else 0
    if countries >= 10:
        return 10
    elif countries >= 5:
        return 7
    elif countries >= 3:
        return 5
    elif countries >= 1:
        return 3
    else:
        return 1


def score_ma(company: Company) -> int:
    """Calculate M&A activity score."""
    acquisitions = len(company.acquisitions) if company.acquisitions else 0
    if acquisitions >= 5:
        return 10
    elif acquisitions >= 3:
        return 7
    elif acquisitions >= 1:
        return 4
    else:
        return 1


def interpret_funding(company: Company) -> str:
    """Interpret funding score."""
    score = score_funding(company)
    if score >= 7:
        return "Strong funding backing"
    elif score >= 4:
        return "Moderate funding"
    else:
        return "Limited funding"


def interpret_employee_growth(company: Company) -> str:
    """Interpret employee growth."""
    score = score_employee_growth(company)
    if score >= 7:
        return "Rapid hiring"
    elif score >= 4:
        return "Steady growth"
    else:
        return "Slow hiring"


def interpret_geographic(company: Company) -> str:
    """Interpret geographic expansion."""
    score = score_geographic(company)
    if score >= 7:
        return "Global presence"
    elif score >= 4:
        return "Regional expansion"
    else:
        return "Limited expansion"


def interpret_ma(company: Company) -> str:
    """Interpret M&A activity."""
    score = score_ma(company)
    if score >= 7:
        return "Active acquirer"
    elif score >= 4:
        return "Some acquisitions"
    else:
        return "No M&A"


def interpret_saas(company: Company) -> str:
    """Interpret SaaS maturity."""
    score = company.saas_maturity or 0
    if score >= 8:
        return "Cloud-native"
    elif score >= 5:
        return "Hybrid"
    else:
        return "On-premise"
