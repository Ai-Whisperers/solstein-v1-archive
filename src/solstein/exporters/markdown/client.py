"""Client report generator for competitive analysis.

Extracted from generator.py as part of EPIC-021 file splitting.
Generates comprehensive client reports with competitive analysis.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from loguru import logger

from solstein.domain.models import Company
from solstein.analytics.constants import derive_threat_level

from .base import BaseReportGenerator, ReportFormatter
from .company import CompanyReportGenerator
from .helpers import (
    score_funding,
    score_employee_growth,
    score_geographic,
    score_ma,
    interpret_funding,
    interpret_employee_growth,
    interpret_geographic,
    interpret_ma,
)


class ClientReportGenerator(CompanyReportGenerator):
    """Extended report generator for client-specific reports."""

    def generate_client_report(
        self,
        client_company: Company,
        competitors: list[Company],
        output_dir: Path | None = None,
    ) -> dict[str, Path]:
        """Generate complete client report with competitive analysis."""
        output_dir = output_dir or self.output_dir / self.formatter.sanitize_filename(client_company.name)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated = {}

        # Generate individual company reports
        generated.update(self.generate_company_reports(client_company, output_dir))

        # Generate competitive analysis
        generated["competitive_analysis"] = self._generate_competitive_analysis(client_company, competitors, output_dir)

        # Generate market overview for this client's market
        from .market import MarketReportGenerator

        market_gen = MarketReportGenerator(output_dir)
        generated["market_overview"] = market_gen.generate_market_overview(competitors + [client_company], output_dir)

        logger.info(f"Generated client report for {client_company.name} in {output_dir}")
        return generated

    def _generate_competitive_analysis(self, client: Company, competitors: list[Company], output_dir: Path) -> Path:
        """Generate competitive analysis report."""

        # Sort competitors by score
        sorted_comp = sorted(competitors, key=lambda c: c.composite_score or 0, reverse=True)

        # Find direct competitors (similar tier/score)
        direct = [c for c in sorted_comp if c.tier == client.tier and c.id != client.id][:5]

        # Find threats (higher score competitors)
        threats = [c for c in sorted_comp if (c.composite_score or 0) > (client.composite_score or 0)][:5]

        def _fmt_float(value: float | None) -> str:
            if value is None:
                return "N/A"
            return f"{value:.1f}"

        ai_market_avg = self._avg([c.ai_score for c in competitors if c.ai_score is not None]) if competitors else None

        growth_market_avg = (
            self._avg([c.growth_score for c in competitors if c.growth_score is not None]) if competitors else None
        )
        growth_top = max([c.growth_score or 0 for c in competitors], default=None) if competitors else None

        health_market_avg = (
            self._avg([c.financial_health_score for c in competitors if c.financial_health_score is not None])
            if competitors
            else None
        )
        health_top = max([c.financial_health_score or 0 for c in competitors], default=None) if competitors else None

        position_market_avg = (
            self._avg([c.competitive_position_score for c in competitors if c.competitive_position_score is not None])
            if competitors
            else None
        )
        position_top = (
            max([c.competitive_position_score or 0 for c in competitors], default=None) if competitors else None
        )

        composite_market_avg = (
            self._avg([c.composite_score for c in competitors if c.composite_score is not None])
            if competitors
            else None
        )
        composite_top = max([c.composite_score or 0 for c in competitors], default=None) if competitors else None

        # Check data authenticity and add warning if synthetic data detected
        is_authentic, warning = self._check_data_authenticity([client] + competitors)

        report = f"""# Competitive Analysis - {client.name}

{warning if warning else ""}
**Report Date**: {datetime.now().strftime("%B %Y")}

**Report Date**: {datetime.now().strftime("%B %Y")}
**Client**: {client.name}
**Analysis Scope**: {len(competitors)} competitors

---

## Executive Summary

This report analyzes {client.name}'s competitive position against {len(competitors)}
companies in the {client.industry or "energy software"} market.

### Key Findings

- **Current Position**: {client.classification or "N/A"} ({client.composite_score or "N/A"}/10)
- **Revenue**: €{client.financials.revenue or 0:.1f}M (CAGR: {client.revenue_cagr_3yr or "N/A"}%)
- **Competitive Threats**: {len(threats)} companies with higher composite scores
- **AI Gap**: {client.ai_score or 0}/10 (Market avg: {_fmt_float(ai_market_avg)})

---

## Client Profile

| Metric | Value | Market Rank |
|---|---|---|
| Revenue | €{client.financials.revenue or 0:.1f}M | {self._rank_revenue(client, competitors)} |
| Growth (CAGR) | {client.revenue_cagr_3yr or "N/A"}% | {self._rank_growth(client, competitors)} |
| Composite Score | {client.composite_score or "N/A"} | {self._rank_score(client, competitors)} |
| AI Score | {client.ai_score or "N/A"}/10 | {self._rank_ai(client, competitors)} |
| SaaS Maturity | {client.saas_maturity or "N/A"}/10 | {self._rank_saas(client, competitors)} |

---

## Competitive Positioning

### Score Comparison

| Dimension | {client.name} | Market Avg | Top Performer |
|---|---|---|---|
| Growth Score | {client.growth_score or "N/A"} | {_fmt_float(growth_market_avg)} | {_fmt_float(growth_top)} |
| Financial Health | {client.financial_health_score or "N/A"} | {_fmt_float(health_market_avg)} | {_fmt_float(health_top)} |
| Competitive Position | {self.formatter.format_score(client.competitive_position_score)} | {_fmt_float(position_market_avg)} | {_fmt_float(position_top)} |
| Composite | {client.composite_score or "N/A"} | {_fmt_float(composite_market_avg)} | {_fmt_float(composite_top)} |
| Revenue CAGR | {client.revenue_cagr_3yr or "N/A"}% | {self._avg([c.revenue_cagr_3yr for c in sorted_comp if c.revenue_cagr_3yr]):.1f}% | {max([c.revenue_cagr_3yr for c in sorted_comp if c.revenue_cagr_3yr], default=0):.1f}% |

---

## Direct Competitors

These companies operate in the same tier with similar market positioning:

| Company | Revenue | CAGR | Score | AI | SaaS | Classification |
|---|---|---|---|---|---|---|
"""
        for c in direct:
            report += f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {c.composite_score or 'N/A'} | {c.ai_score or 'N/A'}/10 | {c.saas_maturity or 'N/A'}/10 | {c.classification or 'N/A'} |\n"

        # Add detailed competitor analysis
        if direct:
            report += """

### Competitor Details

"""
            for c in direct:
                report += f"""**{c.name}** ({c.classification or "Unknown"})
- Revenue: €{c.financials.revenue or 0:.1f}M | CAGR: {c.revenue_cagr_3yr or "N/A"}% | Score: {c.composite_score or "N/A"}/10
- AI Maturity: {c.ai_score or "N/A"}/10 | SaaS Maturity: {c.saas_maturity or "N/A"}/10
"""
                # Add relative positioning
                if c.composite_score and client.composite_score:
                    diff = c.composite_score - client.composite_score
                    if diff > 0:
                        report += f"- **{diff:.2f} points higher** composite score\n"
                    elif diff < 0:
                        report += f"- **{abs(diff):.2f} points lower** composite score\n"

                # Add key differentiator
                if c.ai_score and client.ai_score and c.ai_score > client.ai_score:
                    report += f"- **AI Advantage**: {c.ai_score}/10 vs your {client.ai_score}/10\n"
                if c.saas_maturity and client.saas_maturity and c.saas_maturity > client.saas_maturity:
                    report += f"- **SaaS Advantage**: {c.saas_maturity}/10 vs your {client.saas_maturity}/10\n"
                if c.revenue_cagr_3yr and client.revenue_cagr_3yr and c.revenue_cagr_3yr > client.revenue_cagr_3yr:
                    report += f"- **Growth Advantage**: {c.revenue_cagr_3yr}% CAGR vs your {client.revenue_cagr_3yr}%\n"

                report += "\n"

        report += """

## Competitive Threats

Companies with superior composite scores that could disrupt market position:

| Company | Revenue | CAGR | Score | Threat Level |
|---|---|---|---|---|
"""
        if threats:
            for c in threats:
                score_diff = (c.composite_score or 0) - (client.composite_score or 0)
                threat = "High" if score_diff > 2 else "Medium" if score_diff > 1 else "Low"
                report += f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {c.composite_score or 'N/A'} | {threat} |\n"
        else:
            report += "| *No companies with higher scores* | - | - | - | *N/A* |\n"

        # Add all competitors section
        report += """

## Competitive Landscape

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
            report += f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {c.composite_score or 'N/A'} | {diff_str} |\n"

        report += f"""

## Strategic Recommendations

### Strengths to Leverage

{self._generate_client_strengths(client, competitors)}

### Weaknesses to Address

{self._generate_client_weaknesses(client, competitors)}

### Opportunities

1. Target competitors with lower AI scores for market share gains
2. Expand geographically to markets served by weaker competitors
3. Acquire AI capabilities from smaller players

### Threats to Monitor

- {threats[0].name if threats else "N/A"} - Highest scoring competitor
- {"; ".join([c.name for c in threats[:3]]) if threats else "None identified"}

---

## Appendix: All Competitors

| Company | Revenue | CAGR | AI | SaaS | Classification | Threat Level |
|---|---|---|---|---|---|---|
"""
        for c in sorted_comp:
            threat = derive_threat_level(c.classification, c.composite_score or 0)
            report += f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {c.ai_score or 'N/A'}/10 | {c.saas_maturity or 'N/A'}/10 | {c.classification or 'N/A'} | {threat} |\n"

        report += f"""

---

*Report generated by SolStein Competitive Intelligence Platform*
*Data as of {datetime.now().strftime("%B %Y")}*
"""
        output_path = output_dir / "competitive-analysis.md"
        output_path.write_text(report)
        return output_path

    def _rank_revenue(self, client: Company, competitors: list[Company]) -> str:
        """Get revenue rank."""
        all_comp = competitors + [client]
        sorted_comp = sorted(
            [c for c in all_comp if c.financials.revenue],
            key=lambda c: c.financials.revenue or 0,
            reverse=True,
        )
        rank = next((i + 1 for i, c in enumerate(sorted_comp) if c.id == client.id), "N/A")
        return f"{rank}/{len(sorted_comp)}"

    def _rank_growth(self, client: Company, competitors: list[Company]) -> str:
        """Get growth rank."""
        all_comp = competitors + [client]
        sorted_comp = sorted(
            [c for c in all_comp if c.revenue_cagr_3yr],
            key=lambda c: c.revenue_cagr_3yr or 0,
            reverse=True,
        )
        rank = next((i + 1 for i, c in enumerate(sorted_comp) if c.id == client.id), "N/A")
        return f"{rank}/{len(sorted_comp)}"

    def _rank_score(self, client: Company, competitors: list[Company]) -> str:
        """Get score rank."""
        all_comp = competitors + [client]
        sorted_comp = sorted(
            [c for c in all_comp if c.composite_score],
            key=lambda c: c.composite_score or 0,
            reverse=True,
        )
        rank = next((i + 1 for i, c in enumerate(sorted_comp) if c.id == client.id), "N/A")
        return f"{rank}/{len(sorted_comp)}"

    def _rank_ai(self, client: Company, competitors: list[Company]) -> str:
        """Get AI score rank."""
        all_comp = competitors + [client]
        sorted_comp = sorted(
            [c for c in all_comp if c.ai_score is not None],
            key=lambda c: c.ai_score or 0,
            reverse=True,
        )
        rank = next((i + 1 for i, c in enumerate(sorted_comp) if c.id == client.id), "N/A")
        return f"{rank}/{len(sorted_comp)}"

    def _rank_saas(self, client: Company, competitors: list[Company]) -> str:
        """Get SaaS maturity rank."""
        all_comp = competitors + [client]
        sorted_comp = sorted(
            [c for c in all_comp if c.saas_maturity],
            key=lambda c: c.saas_maturity or 0,
            reverse=True,
        )
        rank = next((i + 1 for i, c in enumerate(sorted_comp) if c.id == client.id), "N/A")
        return f"{rank}/{len(sorted_comp)}"

    def _generate_client_strengths(self, client: Company, competitors: list[Company]) -> str:
        """Generate client strengths."""
        client_score = client.composite_score or 0
        market_avg = self._avg([c.composite_score for c in competitors if c.composite_score])

        strengths = []
        if client_score > market_avg + 1:
            strengths.append(f"Superior composite score ({client_score:.1f} vs {market_avg:.1f} market avg)")

        if client.saas_maturity:
            avg_saas = self._avg([c.saas_maturity for c in competitors if c.saas_maturity])
            if client.saas_maturity > avg_saas + 1:
                strengths.append(f"Advanced SaaS maturity ({client.saas_maturity} vs {avg_saas:.1f} avg)")

        if client.ai_score:
            avg_ai = self._avg([c.ai_score for c in competitors if c.ai_score is not None])
            if client.ai_score > avg_ai:
                strengths.append(f"Strong AI position ({client.ai_score}/10 vs {avg_ai:.1f} avg)")

        return "\n".join([f"- {s}" for s in strengths]) if strengths else "- No significant strengths identified"

    def _generate_client_weaknesses(self, client: Company, competitors: list[Company]) -> str:
        """Generate client weaknesses."""
        weaknesses = []
        classification = getattr(client, "classification", None)

        # AI gap analysis
        if client.ai_score is not None:
            avg_ai = self._avg([c.ai_score for c in competitors if c.ai_score is not None])
            if client.ai_score < avg_ai - 1:
                weaknesses.append(f"AI capability gap ({client.ai_score}/10 vs {avg_ai:.1f} market avg)")
            elif client.ai_score < avg_ai - 0.5:
                weaknesses.append(f"Below-average AI maturity ({client.ai_score}/10)")
            elif client.ai_score < 5:
                weaknesses.append(
                    f"Limited AI adoption ({client.ai_score}/10) - opportunity for digital transformation"
                )

        # SaaS maturity gaps
        if client.saas_maturity:
            avg_saas = self._avg([c.saas_maturity for c in competitors if c.saas_maturity])
            if client.saas_maturity < avg_saas - 1:
                weaknesses.append(f"SaaS maturity gap ({client.saas_maturity} vs {avg_saas:.1f} avg)")
            elif client.saas_maturity < 5:
                weaknesses.append(f"Legacy technology stack (SaaS: {client.saas_maturity}/10)")

        # Financial/market position gaps
        client_score = client.composite_score or 0
        market_avg = self._avg([c.composite_score for c in competitors if c.composite_score])
        if client_score < market_avg - 1:
            weaknesses.append(f"Below-market composite score ({client_score:.1f} vs {market_avg:.1f} avg)")
        elif classification == "Lead":
            weaknesses.append(f"Legacy classification ({client_score:.1f}/10) - transformation opportunity")

        if not client.latest_valuation_eur:
            weaknesses.append("No disclosed valuation (competitors have clearer market positioning)")

        if not client.total_funding_raised_eur and any(c.total_funding_raised_eur for c in competitors):
            weaknesses.append("Bootstrapped/unfunded vs. funded competitors")

        # Growth concerns
        if client.revenue_cagr_3yr is not None and client.revenue_cagr_3yr < 5:
            weaknesses.append(f"Low growth trajectory ({client.revenue_cagr_3yr}% CAGR)")

        # For Phoenix/high-performing companies, show strategic considerations instead of weaknesses
        if classification == "Phoenix" and not weaknesses:
            weaknesses.append(f"**Strategic Position**: Phoenix-class company ({client_score:.1f}/10)")
            # Add market leadership risks
            threats = [c for c in competitors if (c.composite_score or 0) > (client.composite_score or 0)]
            if threats:
                weaknesses.append(f"Market leadership challenged by {len(threats)} higher-scoring competitor(s)")
            else:
                weaknesses.append("Market leader - maintain innovation edge to defend position")

            # Add scale-based considerations
            revenue = getattr(client.financials, "revenue", 0) or 0
            if revenue < 10:
                weaknesses.append(f"High-growth but small scale (€{revenue:.1f}M) - execution risk at scale")

        if weaknesses:
            return "\n".join([f"- {w}" for w in weaknesses])
        else:
            return f"- Market-competitive position across key metrics (score: {client_score:.1f}/10)"

    def _avg(self, values: list) -> float:
        """Calculate average."""
        values = [v for v in values if v is not None and v != float("inf")]
        return sum(values) / len(values) if values else 0
