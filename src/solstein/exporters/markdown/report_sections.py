"""Report section generators for competitive analysis.

EPIC-020: Extracted from _generate_competitive_analysis function.
Each method generates one section of the competitive analysis report.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from solstein.domain.models import Company


class _FormatterLike(Protocol):
    def format_score(self, value: float | None) -> str: ...


def _fmt_float(value: float | None) -> str:
    """Format float value."""
    return f"{value:.2f}" if value is not None else "N/A"


class ReportSectionGenerator:
    """Generate individual sections of the competitive analysis report."""

    def __init__(self, formatter: _FormatterLike):
        self.formatter = formatter

    def generate_executive_summary(
        self,
        client: Company,
        competitors: list[Company],
        threats: list[Company],
        ai_market_avg: float | None,
        warning: str | None,
    ) -> str:
        """Generate executive summary section."""
        return f"""# Competitive Analysis - {client.name}

{warning if warning else ""}
**Report Date**: {datetime.now().strftime("%B %Y")}

**Client**: {client.name}
**Analysis Scope**: {len(competitors)} competitors

---

## Executive Summary

This report analyzes {client.name}'s competitive position against {len(competitors)}
companies in the {client.industry or "energy software"} market.

### Key Findings

- **Current Position**: {client.classification or "N/A"} ({_fmt_float(client.composite_score)}/10)
- **Revenue**: €{client.financials.revenue or 0:.1f}M (CAGR: {client.revenue_cagr_3yr or "N/A"}%)
- **Competitive Threats**: {len(threats)} companies with higher composite scores
- **AI Gap**: {_fmt_float(client.ai_score)}/10 (Market avg: {_fmt_float(ai_market_avg)})

---
"""

    def generate_client_profile(
        self,
        client: Company,
        competitors: list[Company],
        rank_revenue_fn: Callable[[Company, list[Company]], object],
        rank_growth_fn: Callable[[Company, list[Company]], object],
        rank_score_fn: Callable[[Company, list[Company]], object],
        rank_ai_fn: Callable[[Company, list[Company]], object],
        rank_saas_fn: Callable[[Company, list[Company]], object],
    ) -> str:
        """Generate client profile section."""
        return f"""## Client Profile

| Metric | Value | Market Rank |
|---|---|---|
| Revenue | €{client.financials.revenue or 0:.1f}M | {rank_revenue_fn(client, competitors)} |
| Growth (CAGR) | {client.revenue_cagr_3yr or "N/A"}% | {rank_growth_fn(client, competitors)} |
| Composite Score | {_fmt_float(client.composite_score)} | {rank_score_fn(client, competitors)} |
| AI Score | {_fmt_float(client.ai_score)}/10 | {rank_ai_fn(client, competitors)} |
| SaaS Maturity | {_fmt_float(client.saas_maturity)}/10 | {rank_saas_fn(client, competitors)} |

---
"""

    def generate_competitive_positioning(
        self,
        client: Company,
        competitors: list[Company],
        growth_market_avg: float | None,
        growth_top: float | None,
        health_market_avg: float | None,
        health_top: float | None,
        position_market_avg: float | None,
        position_top: float | None,
        composite_market_avg: float | None,
        composite_top: float | None,
    ) -> str:
        """Generate competitive positioning section."""
        sorted_comp = sorted(
            [c for c in competitors if c.composite_score is not None],
            key=lambda c: c.composite_score or 0,
            reverse=True,
        )

        return f"""## Competitive Positioning

### Score Comparison

| Dimension | {client.name} | Market Avg | Top Performer |
|---|---|---|---|
| Growth Score | {_fmt_float(client.growth_score)} | {_fmt_float(growth_market_avg)} | {_fmt_float(growth_top)} |
| Financial Health | {_fmt_float(client.financial_health_score)} | {_fmt_float(health_market_avg)} | {_fmt_float(health_top)} |
| Competitive Position | {self.formatter.format_score(client.competitive_position_score)} | {_fmt_float(position_market_avg)} | {_fmt_float(position_top)} |
| Composite | {_fmt_float(client.composite_score)} | {_fmt_float(composite_market_avg)} | {_fmt_float(composite_top)} |
| Revenue CAGR | {client.revenue_cagr_3yr or "N/A"}% | {self._avg([c.revenue_cagr_3yr for c in sorted_comp if c.revenue_cagr_3yr]):.1f}% | {max([c.revenue_cagr_3yr for c in sorted_comp if c.revenue_cagr_3yr], default=0):.1f}% |

---
"""

    def _avg(self, values: list[float | None]) -> float:
        """Calculate average of non-None values."""
        valid = [v for v in values if v is not None]
        return sum(valid) / len(valid) if valid else 0.0

    def generate_direct_competitors(
        self,
        client: Company,
        direct: list[Company],
    ) -> str:
        """Generate direct competitors section."""
        section = """## Direct Competitors

These companies operate in the same tier with similar market positioning:

| Company | Revenue | CAGR | Score | AI | SaaS | Classification |
|---|---|---|---|---|---|---|
"""
        for c in direct:
            section += f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {_fmt_float(c.composite_score)} | {_fmt_float(c.ai_score)}/10 | {_fmt_float(c.saas_maturity)}/10 | {c.classification or 'N/A'} |\n"

        return section

    def generate_competitor_details(
        self,
        client: Company,
        direct: list[Company],
    ) -> str:
        """Generate detailed competitor analysis."""
        if not direct:
            return ""

        section = """
### Competitor Details

"""
        for c in direct:
            section += f"""**{c.name}** ({c.classification or "Unknown"})
- Revenue: €{c.financials.revenue or 0:.1f}M | CAGR: {c.revenue_cagr_3yr or "N/A"}% | Score: {_fmt_float(c.composite_score)}/10
- AI Maturity: {_fmt_float(c.ai_score)}/10 | SaaS Maturity: {_fmt_float(c.saas_maturity)}/10
"""
            # Add relative positioning
            if c.composite_score and client.composite_score:
                diff = c.composite_score - client.composite_score
                if diff > 0:
                    section += f"- **{diff:.2f} points higher** composite score\n"
                elif diff < 0:
                    section += f"- **{abs(diff):.2f} points lower** composite score\n"

            # Add key differentiator
            if c.ai_score and client.ai_score and c.ai_score > client.ai_score:
                section += f"- **AI Advantage**: {_fmt_float(c.ai_score)}/10 vs your {_fmt_float(client.ai_score)}/10\n"
            if c.saas_maturity and client.saas_maturity and c.saas_maturity > client.saas_maturity:
                section += f"- **SaaS Advantage**: {_fmt_float(c.saas_maturity)}/10 vs your {_fmt_float(client.saas_maturity)}/10\n"
            if c.revenue_cagr_3yr and client.revenue_cagr_3yr and c.revenue_cagr_3yr > client.revenue_cagr_3yr:
                section += f"- **Growth Advantage**: {c.revenue_cagr_3yr:.1f}% CAGR vs your {client.revenue_cagr_3yr:.1f}%\n"

            section += "\n"

        return section

    def generate_competitive_threats(
        self,
        client: Company,
        threats: list[Company],
    ) -> str:
        """Generate competitive threats section."""
        section = """## Competitive Threats

Companies with superior composite scores that could disrupt market position:

| Company | Revenue | CAGR | Score | Threat Level |
|---|---|---|---|---|
"""
        if threats:
            for c in threats:
                score_diff = (c.composite_score or 0) - (client.composite_score or 0)
                threat = "High" if score_diff > 2 else "Medium" if score_diff > 1 else "Low"
                section += f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {_fmt_float(c.composite_score)} | {threat} |\n"
        else:
            section += "| *No companies with higher scores* | - | - | - | *N/A* |\n"

        return section

    def generate_competitive_landscape(
        self,
        client: Company,
        sorted_comp: list[Company],
    ) -> str:
        """Generate competitive landscape section."""
        section = """## Competitive Landscape

All competitors ranked by composite score:

| Company | Revenue | CAGR | Score | vs Client |
|---|---|---|---|---|
"""
        all_comp = [c for c in sorted_comp if c.id != client.id][:5]
        for c in all_comp:
            score_diff = (c.composite_score or 0) - (client.composite_score or 0)
            if score_diff > 0:
                diff_str = f"+{score_diff:.2f} (higher)"
            elif score_diff < 0:
                diff_str = f"{score_diff:.2f} (lower)"
            else:
                diff_str = "0.00 (equal)"
            section += f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {_fmt_float(c.composite_score)} | {diff_str} |\n"

        return section

    def generate_strategic_recommendations(
        self,
        client: Company,
        competitors: list[Company],
        threats: list[Company],
        strengths_fn: Callable[[Company, list[Company]], str],
        weaknesses_fn: Callable[[Company, list[Company]], str],
    ) -> str:
        """Generate strategic recommendations section."""
        return f"""## Strategic Recommendations

### Strengths to Leverage

{strengths_fn(client, competitors)}

### Weaknesses to Address

{weaknesses_fn(client, competitors)}

### Opportunities

1. Target competitors with lower AI scores for market share gains
2. Expand geographically to markets served by weaker competitors
3. Acquire AI capabilities from smaller players

### Threats to Monitor

- {threats[0].name if threats else "N/A"} - Highest scoring competitor
- {"; ".join([c.name for c in threats[:3]]) if threats else "None identified"}

---
"""

    def generate_appendix(
        self,
        sorted_comp: list[Company],
        derive_threat_level_fn: Callable[[str | None, float], str],
    ) -> str:
        """Generate appendix section."""
        section = """## Appendix: All Competitors

| Company | Revenue | CAGR | AI | SaaS | Classification | Threat Level |
|---|---|---|---|---|---|---|
"""
        for c in sorted_comp:
            threat = derive_threat_level_fn(c.classification, c.composite_score or 0)
            section += f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {_fmt_float(c.ai_score)}/10 | {_fmt_float(c.saas_maturity)}/10 | {c.classification or 'N/A'} | {threat} |\n"

        section += f"""

---

*Report generated by SolStein Competitive Intelligence Platform*
*Data as of {datetime.now().strftime("%B %Y")}*
"""
        return section
