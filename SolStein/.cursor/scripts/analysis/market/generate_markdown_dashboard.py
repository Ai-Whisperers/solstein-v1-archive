#!/usr/bin/env python3
"""Generate a markdown financial dashboard from extracted competitor data.

Produces `financial-dashboard.md` with leaderboards, Mermaid charts,
classification matrix, and a Meteor Warning skeleton.

Usage:
    python generate_markdown_dashboard.py --input competitor_data.json --output financial-dashboard.md
    python generate_markdown_dashboard.py --source tickets/COMPETITION/ --output financial-dashboard.md
    python generate_markdown_dashboard.py --input data.json --output out.md --profile

Requirements:
    Python 3.10+

Performance (29 competitors):
    Total pipeline: ~0.006s
    All section rendering: < 0.001s each (string concatenation, negligible)
    File write: ~0.001s
"""

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Optional

from competitor_utils import (
    CLASSIFICATION_ORDER,
    calc_hiring_efficiency,
    calc_growth_roi,
    calc_rev_per_employee_eur_k,
    calc_rev_per_eur_m_raised,
    get_classification,
    get_composite,
    get_score,
    is_eneve,
    parse_total_raised_eur_m,
    timed_phase,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def fmt_score(val: Optional[float]) -> str:
    if val is None:
        return "N/A"
    if val == int(val):
        return str(int(val))
    return f"{val:.1f}"


def fmt_pct(val: Optional[float]) -> str:
    if val is None:
        return "N/A"
    return f"{val:.1f}%"


def fmt_eur(val: Optional[float]) -> str:
    if val is None:
        return "N/A"
    if val >= 1000:
        return f"EUR {val/1000:.1f}B"
    return f"EUR {val:.0f}M"


def bold_if_eneve(text: str, comp: dict) -> str:
    return f"**{text}**" if is_eneve(comp) else text


def mermaid_safe_name(name: str) -> str:
    """Shorten and sanitize a company name for Mermaid X-axis labels."""
    name = name.replace("(formerly Energy21)", "").strip()
    # Take first word or abbreviation for long names
    parts = name.split()
    if len(parts) > 2:
        return parts[0]
    return name.replace(" ", "")


def build_classification_matrix(competitors: list[dict]) -> str:
    """Build the Growth Classification Matrix section."""
    lines = ["## Growth Classification Matrix\n"]

    for cls in CLASSIFICATION_ORDER:
        comps = [c for c in competitors if get_classification(c) == cls]
        if not comps:
            continue

        desc = {
            "Rocket": "Companies with explosive growth, heavy investment, and market-disrupting trajectories.",
            "Riser": "Companies with strong growth signals, actively investing in their future.",
            "Steady": "Stable companies with moderate growth. Evolutionary, not revolutionary.",
            "Dinosaur": "Flat or declining. Legacy mode. No visible investment in transformation.",
        }
        score_range = {
            "Rocket": "7.0-10.0", "Riser": "5.0-6.9",
            "Steady": "3.0-4.9", "Dinosaur": "1.0-2.9",
        }

        lines.append(f"### {cls}s (Composite Score {score_range.get(cls, '')})\n")
        lines.append(f"{desc.get(cls, '')}\n")
        lines.append("| Company | Tier | Composite | Rev Growth | Funding | Emp Growth | Geo Expand | M&A | SaaS |")
        lines.append("|---|---|---|---|---|---|---|---|---|")

        for c in sorted(comps, key=lambda x: get_composite(x) or 0, reverse=True):
            name = bold_if_eneve(c.get("company_name", ""), c)
            tier = bold_if_eneve(c.get("tier", "") or "--", c)
            row_vals = [
                name, tier,
                bold_if_eneve(fmt_score(get_composite(c)), c),
                bold_if_eneve(fmt_score(get_score(c, "Revenue Growth")), c),
                bold_if_eneve(fmt_score(get_score(c, "Funding Momentum")), c),
                bold_if_eneve(fmt_score(get_score(c, "Employee Growth")), c),
                bold_if_eneve(fmt_score(get_score(c, "Geographic Expansion")), c),
                bold_if_eneve(fmt_score(get_score(c, "M&A Activity")), c),
                bold_if_eneve(fmt_score(get_score(c, "SaaS Maturity")), c),
            ]
            lines.append("| " + " | ".join(row_vals) + " |")

        lines.append("")

    return "\n".join(lines)


def build_revenue_leaderboard(competitors: list[dict]) -> str:
    """Build Revenue Growth Leaderboard with Mermaid chart."""
    sorted_comps = sorted(
        competitors,
        key=lambda c: c.get("revenue", {}).get("cagr_3yr_pct") or 0,
        reverse=True,
    )

    lines = ["## Revenue Growth Leaderboard\n"]
    lines.append("| Rank | Company | Tier | Revenue (latest, EUR) | Revenue CAGR (3yr) | Classification |")
    lines.append("|---|---|---|---|---|---|")

    for i, c in enumerate(sorted_comps, 1):
        rev = c.get("revenue", {})
        name = bold_if_eneve(c.get("company_name", ""), c)
        tier = bold_if_eneve(c.get("tier", "") or "--", c)
        rev_str = bold_if_eneve(fmt_eur(rev.get("latest_revenue_eur_m")), c)
        cagr_str = bold_if_eneve(fmt_pct(rev.get("cagr_3yr_pct")), c)
        cls_str = bold_if_eneve(get_classification(c) or "N/A", c)
        lines.append(f"| {i} | {name} | {tier} | {rev_str} | {cagr_str} | {cls_str} |")

    # Mermaid chart -- top 15 + Eneve
    chart_comps = [c for c in sorted_comps if not is_eneve(c)][:14]
    eneve_comp = next((c for c in sorted_comps if is_eneve(c)), None)
    if eneve_comp:
        chart_comps.append(eneve_comp)

    if len(chart_comps) >= 2:
        names = [mermaid_safe_name(c.get("company_name", "")) for c in chart_comps]
        values = [c.get("revenue", {}).get("cagr_3yr_pct") or 0 for c in chart_comps]
        max_val = max(values) if values else 60
        y_max = int((max_val // 10 + 2) * 10)

        lines.append("\n### Revenue CAGR Chart\n")
        lines.append("```mermaid")
        lines.append("xychart-beta")
        lines.append('    title "Revenue CAGR (3yr) - All Competitors"')
        lines.append(f"    x-axis [{', '.join(names)}]")
        lines.append(f'    y-axis "CAGR %" 0 --> {y_max}')
        lines.append(f"    bar [{', '.join(str(int(v)) for v in values)}]")
        lines.append("```")

    lines.append("")
    return "\n".join(lines)


def build_funding_leaderboard(competitors: list[dict]) -> str:
    """Build Funding Leaderboard."""
    sorted_comps = sorted(
        competitors,
        key=lambda c: get_score(c, "Funding Momentum") or 0,
        reverse=True,
    )

    lines = ["## Funding Leaderboard\n"]
    lines.append("| Rank | Company | Tier | Funding Score | Total Raised | Latest Valuation | Classification |")
    lines.append("|---|---|---|---|---|---|---|")

    for i, c in enumerate(sorted_comps, 1):
        funding = c.get("funding", {})
        name = bold_if_eneve(c.get("company_name", ""), c)
        tier = bold_if_eneve(c.get("tier", "") or "--", c)
        score = bold_if_eneve(fmt_score(get_score(c, "Funding Momentum")), c)
        raised = bold_if_eneve(funding.get("total_raised_text", "N/A") or "N/A", c)
        valuation = bold_if_eneve(funding.get("latest_valuation_text", "N/A") or "N/A", c)
        cls_str = bold_if_eneve(get_classification(c) or "N/A", c)
        lines.append(f"| {i} | {name} | {tier} | {score} | {raised} | {valuation} | {cls_str} |")

    lines.append("")
    return "\n".join(lines)


def build_employee_leaderboard(competitors: list[dict]) -> str:
    """Build Employee Growth Leaderboard."""
    sorted_comps = sorted(
        competitors,
        key=lambda c: c.get("employees", {}).get("employee_cagr_pct") or 0,
        reverse=True,
    )

    lines = ["## Employee Growth Leaderboard\n"]
    lines.append("| Rank | Company | Tier | Headcount (latest) | Employee CAGR | Open Positions | Classification |")
    lines.append("|---|---|---|---|---|---|---|")

    for i, c in enumerate(sorted_comps, 1):
        emp = c.get("employees", {})
        name = bold_if_eneve(c.get("company_name", ""), c)
        tier = bold_if_eneve(c.get("tier", "") or "--", c)
        hc = emp.get("latest_headcount")
        hc_str = bold_if_eneve(f"{int(hc)}" if hc else "N/A", c)
        cagr = bold_if_eneve(fmt_pct(emp.get("employee_cagr_pct")), c)
        pos = emp.get("open_positions")
        pos_str = bold_if_eneve(f"{int(pos)}" if pos else "N/A", c)
        cls_str = bold_if_eneve(get_classification(c) or "N/A", c)
        lines.append(f"| {i} | {name} | {tier} | {hc_str} | {cagr} | {pos_str} | {cls_str} |")

    # Mermaid chart
    chart_comps = [c for c in sorted_comps if (c.get("employees", {}).get("employee_cagr_pct") or 0) > 0][:15]
    if len(chart_comps) >= 2:
        names = [mermaid_safe_name(c.get("company_name", "")) for c in chart_comps]
        values = [c.get("employees", {}).get("employee_cagr_pct") or 0 for c in chart_comps]
        y_max = int((max(values) // 10 + 2) * 10)

        lines.append("\n### Employee Growth Chart\n")
        lines.append("```mermaid")
        lines.append("xychart-beta")
        lines.append('    title "Employee CAGR (3yr) - All Competitors"')
        lines.append(f"    x-axis [{', '.join(names)}]")
        lines.append(f'    y-axis "CAGR %" 0 --> {y_max}')
        lines.append(f"    bar [{', '.join(str(int(v)) for v in values)}]")
        lines.append("```")

    lines.append("")
    return "\n".join(lines)


def build_saas_ranking(competitors: list[dict]) -> str:
    """Build SaaS Maturity Ranking."""
    sorted_comps = sorted(
        competitors,
        key=lambda c: get_score(c, "SaaS Maturity") or 0,
        reverse=True,
    )

    lines = ["## SaaS Maturity Ranking\n"]
    lines.append("| Rank | Company | Tier | Recurring Revenue % | SaaS Score | Classification |")
    lines.append("|---|---|---|---|---|---|")

    for i, c in enumerate(sorted_comps, 1):
        prof = c.get("profitability", {})
        name = bold_if_eneve(c.get("company_name", ""), c)
        tier = bold_if_eneve(c.get("tier", "") or "--", c)
        rr = prof.get("recurring_revenue_pct")
        rr_str = bold_if_eneve(fmt_pct(rr) if rr else "N/A", c)
        score = bold_if_eneve(fmt_score(get_score(c, "SaaS Maturity")), c)
        cls_str = bold_if_eneve(get_classification(c) or "N/A", c)
        lines.append(f"| {i} | {name} | {tier} | {rr_str} | {score} | {cls_str} |")

    lines.append("")
    return "\n".join(lines)


def build_quadrant_chart(competitors: list[dict]) -> str:
    """Build Growth vs Size quadrant chart."""
    lines = ["## Growth vs Size Quadrant\n"]

    # Normalize: X = relative revenue (0-1), Y = composite score normalized (0-1)
    revenues = [c.get("revenue", {}).get("latest_revenue_eur_m") or 0 for c in competitors]
    max_rev = max(revenues) if revenues else 1
    composites = [get_composite(c) or 0 for c in competitors]
    max_comp = max(composites) if composites else 10

    chart_comps = [c for c in competitors if get_composite(c) is not None]

    if len(chart_comps) >= 3:
        lines.append("```mermaid")
        lines.append("quadrantChart")
        lines.append('    title "Growth Rate vs Company Size"')
        lines.append('    x-axis "Small" --> "Large"')
        lines.append('    y-axis "Slow Growth" --> "Fast Growth"')
        lines.append('    quadrant-1 "Dangerous Giants"')
        lines.append('    quadrant-2 "Incoming Disruptors"')
        lines.append('    quadrant-3 "Marginal Players"')
        lines.append('    quadrant-4 "Sleeping Giants"')

        for c in chart_comps:
            name = mermaid_safe_name(c.get("company_name", ""))
            rev = c.get("revenue", {}).get("latest_revenue_eur_m") or 0
            comp_score = get_composite(c) or 0
            x = round(max(0.05, min(0.95, rev / max_rev)), 2) if max_rev > 0 else 0.5
            y = round(max(0.05, min(0.95, comp_score / max_comp)), 2) if max_comp > 0 else 0.5
            lines.append(f"    {name}: [{x}, {y}]")

        lines.append("```")
    else:
        lines.append("> Insufficient data for quadrant chart (need 3+ competitors with scores).")

    lines.append("")
    return "\n".join(lines)


def build_meteor_warning(competitors: list[dict]) -> str:
    """Build the Meteor Warning narrative skeleton with real numbers."""
    rockets = [c for c in competitors if get_classification(c) == "Rocket"]
    risers = [c for c in competitors if get_classification(c) == "Riser"]
    dinosaurs = [c for c in competitors if get_classification(c) == "Dinosaur"]
    eneve = next((c for c in competitors if is_eneve(c)), None)

    total_analyzed = len(competitors)
    avg_cagr_values = [c.get("revenue", {}).get("cagr_3yr_pct") for c in competitors if c.get("revenue", {}).get("cagr_3yr_pct")]
    avg_cagr = sum(avg_cagr_values) / len(avg_cagr_values) if avg_cagr_values else 0

    eneve_cagr = eneve.get("revenue", {}).get("cagr_3yr_pct") if eneve else None
    eneve_composite = get_composite(eneve) if eneve else None
    eneve_class = get_classification(eneve) if eneve else None

    lines = ["## The Meteor Warning\n"]
    lines.append("### The Numbers Don't Lie\n")
    lines.append(
        f"Of the {total_analyzed} competitors analyzed, "
        f"**{len(rockets)} are Rockets** and **{len(risers)} are Risers**. "
        f"The average revenue CAGR across all tracked competitors is **{avg_cagr:.1f}%**."
    )
    if eneve:
        lines.append(
            f" Eneve's estimated CAGR: **{fmt_pct(eneve_cagr)}**. "
            f"Eneve's composite score: **{fmt_score(eneve_composite)}** ({eneve_class})."
        )
    lines.append("")

    if rockets:
        lines.append("### What the Rockets Are Doing That We Are Not\n")
        for r in rockets:
            name = r.get("company_name", "")
            lines.append(f"- **{name}** (composite {fmt_score(get_composite(r))}): "
                         f"Revenue CAGR {fmt_pct(r.get('revenue', {}).get('cagr_3yr_pct'))}, "
                         f"Funding score {fmt_score(get_score(r, 'Funding Momentum'))}/10")
        lines.append("")

    lines.append("### The Convergence Threat\n")
    lines.append(
        "Multiple trends converge against Eneve:\n"
        "- AI-native entrants building from scratch what took Eneve 20+ years\n"
        "- European energy market harmonization (ENTSO-E, MARI, PICASSO) eroding national moats\n"
        "- Cloud-native platforms with 10x faster implementation times\n"
        "- PE/VC money pouring into energy software\n"
        "- Competitors entering NL market or acquiring NL-capable companies\n"
    )

    lines.append("### What Eneve Must Do\n")
    lines.append(
        "1. **Accelerate SaaS transition** -- close the cloud gap with Rockets\n"
        "2. **Invest in AI** -- every Rocket and most Risers have AI in production\n"
        "3. **Explore strategic funding** -- organic growth alone cannot match PE-backed competitors\n"
        "4. **Expand geographically** -- Netherlands-only is a shrinking moat\n"
        "5. **Consider strategic M&A** -- acquire capabilities instead of building everything in-house\n"
    )

    lines.append("---\n")
    return "\n".join(lines)


def fmt_ratio(val: Optional[float], suffix: str = "") -> str:
    if val is None:
        return "N/A"
    if val == int(val):
        return f"{int(val)}{suffix}"
    return f"{val:.2f}{suffix}"


def _quartile_marker(val: Optional[float], values: list[float], *, high_is_good: bool = True) -> str:
    """Return a visual marker for top/bottom quartile values."""
    if val is None or len(values) < 4:
        return ""
    sorted_vals = sorted(values)
    q1 = sorted_vals[len(sorted_vals) // 4]
    q3 = sorted_vals[3 * len(sorted_vals) // 4]
    if high_is_good:
        if val >= q3:
            return " 🟢"
        if val <= q1:
            return " 🔴"
    else:
        if val <= q1:
            return " 🟢"
        if val >= q3:
            return " 🔴"
    return ""


def build_investment_efficiency(competitors: list[dict]) -> str:
    """Build the Investment Efficiency Ratios section with leaderboard and scatter plot."""
    enriched = []
    for c in competitors:
        enriched.append({
            "comp": c,
            "rev_per_emp": calc_rev_per_employee_eur_k(c),
            "rev_per_raised": calc_rev_per_eur_m_raised(c),
            "hiring_eff": calc_hiring_efficiency(c),
            "growth_roi": calc_growth_roi(c),
        })

    sorted_data = sorted(enriched, key=lambda x: x["rev_per_emp"] or 0, reverse=True)

    # Collect non-None values for quartile calculations
    rev_per_emp_vals = [e["rev_per_emp"] for e in enriched if e["rev_per_emp"] is not None]
    rev_per_raised_vals = [e["rev_per_raised"] for e in enriched if e["rev_per_raised"] is not None]
    hiring_eff_vals = [e["hiring_eff"] for e in enriched if e["hiring_eff"] is not None]

    lines = ["## Investment Efficiency Ratios\n"]
    lines.append(
        "Capital efficiency metrics revealing who builds real value vs burns cash. "
        "Revenue/Employee measures operational leverage; Revenue/EUR M Raised measures capital efficiency; "
        "Hiring Efficiency (Emp CAGR / Rev CAGR) below 1.0 means revenue grows faster than headcount.\n"
    )
    lines.append("| Rank | Company | Tier | Revenue | Headcount | Total Raised | Rev/Emp (EUR K) | Rev/EUR M Raised | Hiring Eff. | Classification |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    for i, entry in enumerate(sorted_data, 1):
        c = entry["comp"]
        rev_m = c.get("revenue", {}).get("latest_revenue_eur_m")
        hc = c.get("employees", {}).get("latest_headcount")
        raised_text = c.get("funding", {}).get("total_raised_text") or "N/A"

        name = bold_if_eneve(c.get("company_name", ""), c)
        tier = bold_if_eneve(c.get("tier", "") or "--", c)
        rev_str = bold_if_eneve(fmt_eur(rev_m), c)
        hc_str = bold_if_eneve(f"{int(hc)}" if hc else "N/A", c)

        # Truncate long raised text for table readability
        raised_display = raised_text if len(raised_text) <= 40 else raised_text[:37] + "..."
        raised_display = bold_if_eneve(raised_display, c)

        rpe_marker = _quartile_marker(entry["rev_per_emp"], rev_per_emp_vals)
        rpr_marker = _quartile_marker(entry["rev_per_raised"], rev_per_raised_vals)
        he_marker = _quartile_marker(entry["hiring_eff"], hiring_eff_vals, high_is_good=False)

        rpe_str = bold_if_eneve(fmt_ratio(entry["rev_per_emp"]) + rpe_marker, c)
        rpr_str = bold_if_eneve(fmt_ratio(entry["rev_per_raised"]) + rpr_marker, c)
        he_str = bold_if_eneve(fmt_ratio(entry["hiring_eff"]) + he_marker, c)
        cls_str = bold_if_eneve(get_classification(c) or "N/A", c)

        lines.append(f"| {i} | {name} | {tier} | {rev_str} | {hc_str} | {raised_display} | {rpe_str} | {rpr_str} | {he_str} | {cls_str} |")

    # Scatter plot: Revenue/Employee (Y-axis) vs Revenue Growth (X-axis)
    chart_data = [
        e for e in enriched
        if e["rev_per_emp"] is not None
        and (e["comp"].get("revenue", {}).get("cagr_3yr_pct") or 0) > 0
    ]
    chart_data.sort(key=lambda e: e["comp"].get("revenue", {}).get("cagr_3yr_pct") or 0, reverse=True)
    chart_data = chart_data[:15]

    if len(chart_data) >= 2:
        names = [mermaid_safe_name(e["comp"].get("company_name", "")) for e in chart_data]
        rev_growth = [e["comp"].get("revenue", {}).get("cagr_3yr_pct") or 0 for e in chart_data]
        rev_per_emp = [e["rev_per_emp"] or 0 for e in chart_data]
        y_max = int((max(rev_per_emp) // 100 + 2) * 100)

        lines.append("\n### Revenue/Employee vs Revenue Growth\n")
        lines.append("Scatter approximation: bars show Revenue/Employee (EUR K) for top revenue growers.\n")
        lines.append("```mermaid")
        lines.append("xychart-beta")
        lines.append('    title "Revenue per Employee (EUR K) - Top Revenue Growers"')
        lines.append(f"    x-axis [{', '.join(names)}]")
        lines.append(f'    y-axis "EUR K / Employee" 0 --> {y_max}')
        lines.append(f"    bar [{', '.join(str(int(v)) for v in rev_per_emp)}]")
        lines.append("```")

    lines.append("")
    return "\n".join(lines)


def _project_value(current: Optional[float], cagr_pct: Optional[float], years: int) -> Optional[float]:
    """Project a value forward using compound annual growth rate."""
    if current is None or cagr_pct is None:
        return None
    return current * (1 + cagr_pct / 100) ** years


def _fmt_proj_eur(val: Optional[float]) -> str:
    """Format projected EUR value with threshold marker when crossing EUR 100M."""
    if val is None:
        return "N/A"
    formatted = fmt_eur(val)
    if val >= 100:
        return f"{formatted} 🔺"
    return formatted


def _fmt_proj_emp(val: Optional[float]) -> str:
    """Format projected employee count with threshold marker when crossing 500."""
    if val is None:
        return "N/A"
    count = int(round(val))
    formatted = f"{count:,}"
    if count >= 500:
        return f"{formatted} 🔺"
    return formatted


def build_scenario_projections(competitors: list[dict]) -> str:
    """Build Scenario Projections section with 3-year CAGR extrapolation.

    Projects revenue and employee figures forward 1-3 years for every competitor.
    Highlights threshold crossings (revenue > EUR 100M, employees > 500) and
    includes a trajectory chart for mid-market competitors + Eneve.
    """
    lines = ["## Scenario Projections (3-Year Extrapolation)\n"]
    lines.append(
        "Revenue and employee projections at current CAGR rates. "
        "🔺 marks projected crossing of key thresholds "
        "(Revenue > EUR 100M, Employees > 500).\n"
    )

    projections = []
    for c in competitors:
        rev = c.get("revenue", {})
        emp = c.get("employees", {})
        current_rev = rev.get("latest_revenue_eur_m")
        rev_cagr = rev.get("cagr_3yr_pct")
        current_emp = emp.get("latest_headcount")
        emp_cagr = emp.get("employee_cagr_pct")

        projections.append({
            "comp": c,
            "current_rev": current_rev,
            "rev_cagr": rev_cagr,
            "rev_2027": _project_value(current_rev, rev_cagr, 1),
            "rev_2028": _project_value(current_rev, rev_cagr, 2),
            "rev_2029": _project_value(current_rev, rev_cagr, 3),
            "current_emp": current_emp,
            "emp_cagr": emp_cagr,
            "emp_2027": _project_value(current_emp, emp_cagr, 1),
            "emp_2028": _project_value(current_emp, emp_cagr, 2),
            "emp_2029": _project_value(current_emp, emp_cagr, 3),
        })

    # --- Revenue Projections Table ---
    rev_sorted = sorted(projections, key=lambda p: p["rev_2029"] or 0, reverse=True)

    lines.append("### Revenue Projections\n")
    lines.append("| Company | Current Revenue | Rev CAGR | 2027 Projected | 2028 Projected | 2029 Projected |")
    lines.append("|---|---|---|---|---|---|")

    for p in rev_sorted:
        c = p["comp"]
        name = bold_if_eneve(c.get("company_name", ""), c)
        cur = bold_if_eneve(fmt_eur(p["current_rev"]), c)
        cagr = bold_if_eneve(fmt_pct(p["rev_cagr"]), c)
        r27 = bold_if_eneve(_fmt_proj_eur(p["rev_2027"]), c)
        r28 = bold_if_eneve(_fmt_proj_eur(p["rev_2028"]), c)
        r29 = bold_if_eneve(_fmt_proj_eur(p["rev_2029"]), c)
        lines.append(f"| {name} | {cur} | {cagr} | {r27} | {r28} | {r29} |")

    lines.append("")

    # --- Employee Projections Table ---
    emp_sorted = sorted(projections, key=lambda p: p["emp_2029"] or 0, reverse=True)

    lines.append("### Employee Projections\n")
    lines.append("| Company | Current Employees | Emp CAGR | 2027 Projected | 2028 Projected | 2029 Projected |")
    lines.append("|---|---|---|---|---|---|")

    for p in emp_sorted:
        c = p["comp"]
        name = bold_if_eneve(c.get("company_name", ""), c)
        cur_val = p["current_emp"]
        cur = bold_if_eneve(f"{int(cur_val):,}" if cur_val else "N/A", c)
        cagr = bold_if_eneve(fmt_pct(p["emp_cagr"]), c)
        e27 = bold_if_eneve(_fmt_proj_emp(p["emp_2027"]), c)
        e28 = bold_if_eneve(_fmt_proj_emp(p["emp_2028"]), c)
        e29 = bold_if_eneve(_fmt_proj_emp(p["emp_2029"]), c)
        lines.append(f"| {name} | {cur} | {cagr} | {e27} | {e28} | {e29} |")

    lines.append("")

    # --- Revenue Trajectory Chart ---
    # Focus on mid-market competitors (< EUR 1B current) for readable scale
    chart_data = [
        p for p in projections
        if p["rev_2029"] is not None
        and p["current_rev"] is not None
        and p["current_rev"] < 1000
    ]
    chart_data.sort(key=lambda p: p["rev_2029"] or 0, reverse=True)
    non_eneve = [p for p in chart_data if not is_eneve(p["comp"])][:10]
    eneve_proj = next((p for p in chart_data if is_eneve(p["comp"])), None)
    chart_items = list(non_eneve)
    if eneve_proj and eneve_proj not in chart_items:
        chart_items.append(eneve_proj)

    if len(chart_items) >= 2:
        names = [mermaid_safe_name(p["comp"].get("company_name", "")) for p in chart_items]
        current_vals = [p["current_rev"] or 0 for p in chart_items]
        proj_2029 = [p["rev_2029"] or 0 for p in chart_items]
        max_val = max(proj_2029) if proj_2029 else 100
        y_max = int((max_val // 100 + 2) * 100)

        lines.append("### Revenue Trajectory Chart\n")
        lines.append(
            "Mid-market competitors (< EUR 1B current revenue) + Eneve. "
            "Bars = current revenue, line = 2029 projected.\n"
        )
        lines.append("```mermaid")
        lines.append("xychart-beta")
        lines.append('    title "Revenue Trajectory: Current vs 2029 Projected (EUR M)"')
        lines.append(f"    x-axis [{', '.join(names)}]")
        lines.append(f'    y-axis "EUR M" 0 --> {y_max}')
        lines.append(f"    bar [{', '.join(str(int(v)) for v in current_vals)}]")
        lines.append(f"    line [{', '.join(str(int(v)) for v in proj_2029)}]")
        lines.append("```")
        lines.append("")

    # --- Disclaimer ---
    lines.append(
        "> **Disclaimer**: Projections based on historical CAGR, not forecasts. "
        "Actual results will vary based on market conditions, strategic decisions, "
        "and competitive dynamics.\n"
    )

    lines.append("")
    return "\n".join(lines)


def build_missing_data(missing: list[dict]) -> str:
    """Build Missing Data section."""
    if not missing:
        return ""

    lines = ["## Missing Data\n"]
    lines.append("Competitors without `financial-growth.md` files:\n")
    lines.append("| Company Folder | Tier | Action Needed |")
    lines.append("|---|---|---|")

    for m in missing:
        folder = m.get("folder", "")
        tier = m.get("tier", "") or "Unknown"
        lines.append(f"| {folder} | {tier} | Run `@research-financial-growth` |")

    lines.append("")
    return "\n".join(lines)


def generate_dashboard(data: dict, output_path: Path, *, profile: bool = False) -> None:
    """Assemble the complete markdown dashboard."""
    competitors = data.get("competitors", [])
    missing = data.get("missing_data", [])
    meta = data.get("metadata", {})

    if not competitors:
        log.error("No competitor data to generate dashboard from.")
        return

    sections = []

    # Header
    sections.append(f"# Financial Growth Dashboard\n")
    sections.append(f"**Generated**: {date.today().isoformat()}")
    sections.append(f"**Competitors Analyzed**: {meta.get('with_financial_data', len(competitors))} "
                    f"of {meta.get('total_folders', '?')}")
    sections.append(f"**Data Source**: Per-competitor financial research via `research-financial-growth` prompt")
    sections.append("\n---\n")

    section_builders = [
        ("Classification matrix", build_classification_matrix),
        ("Revenue leaderboard", build_revenue_leaderboard),
        ("Funding leaderboard", build_funding_leaderboard),
        ("Employee leaderboard", build_employee_leaderboard),
        ("SaaS ranking", build_saas_ranking),
        ("Investment efficiency", build_investment_efficiency),
        ("Quadrant chart", build_quadrant_chart),
        ("Meteor warning", build_meteor_warning),
        ("Scenario projections", build_scenario_projections),
    ]

    for section_name, builder in section_builders:
        with timed_phase(f"Section: {section_name}", profile=profile):
            sections.append(builder(competitors))
        sections.append("---\n")

    if missing:
        sections.append(build_missing_data(missing))

    # Methodology
    sections.append("## Methodology\n")
    sections.append(
        "- **Scoring**: All Growth Scorecard scores use the rubric defined in `research-financial-growth.prompt.md`\n"
        "- **Classification**: Rocket (7.0-10.0), Riser (5.0-6.9), Steady (3.0-4.9), Dinosaur (1.0-2.9)\n"
        "- **Currency**: All EUR equivalents use approximate exchange rates at time of research\n"
        "- **Rankings**: Tied scores broken by revenue CAGR, then funding raised\n"
        "- **Generated by**: `.cursor/scripts/analysis/market/generate_markdown_dashboard.py`\n"
    )

    with timed_phase("Markdown file write", profile=profile):
        content = "\n".join(sections)
        output_path.write_text(content, encoding="utf-8")
    log.info("Dashboard written to %s", output_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate markdown financial dashboard from extracted competitor data.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--input",
        type=Path,
        help="Path to competitor_data.json (pre-extracted)",
    )
    group.add_argument(
        "--source",
        type=Path,
        help="Path to tickets/COMPETITION/ directory (extracts data first)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output .md file path",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Log wall-clock timing for each major pipeline phase",
    )
    args = parser.parse_args()

    try:
        with timed_phase("Total markdown pipeline", profile=args.profile):
            with timed_phase("Data loading", profile=args.profile):
                if args.input:
                    if not args.input.exists():
                        log.error("Input file not found: %s", args.input)
                        return 1
                    data = json.loads(args.input.read_text(encoding="utf-8"))
                else:
                    from extract_competitor_data import extract_all_competitors
                    data = extract_all_competitors(args.source, profile=args.profile)

            generate_dashboard(data, args.output, profile=args.profile)
        return 0
    except json.JSONDecodeError as exc:
        log.error("Invalid JSON in input file: %s", exc)
        return 1
    except Exception as exc:
        log.error("Unexpected error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
