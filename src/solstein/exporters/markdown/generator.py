"""
Markdown report generator for SolStein intelligence reports.

Generates professional reports from Company data - corporate history,
deep analysis, financial growth, and competitive dashboards.
"""

import asyncio
from datetime import datetime
from pathlib import Path

from loguru import logger

from ...domain.models import Company


class ReportGenerator:
    """Generate markdown intelligence reports from Company data."""

    def __init__(self, output_dir: Path | None = None, use_llm: bool = True):
        self.output_dir = output_dir or Path("data/output/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.use_llm = use_llm
        self._llm_enhancer = None
        if use_llm:
            try:
                from ..llm import LLMReportEnhancer

                self._llm_enhancer = LLMReportEnhancer()
            except Exception as e:
                logger.warning(f"LLM enhancer not available: {e}")

    def generate_all_reports(self, companies: list[Company], output_subdir: str | None = None) -> dict[str, Path]:
        """Generate all report types for all companies."""
        if output_subdir:
            report_dir = self.output_dir / output_subdir
        else:
            report_dir = self.output_dir
        report_dir.mkdir(parents=True, exist_ok=True)

        generated = {}

        for company in companies:
            company_reports = self.generate_company_reports(company, report_dir)
            generated[company.name] = company_reports

        # Generate market overview if multiple companies
        if len(companies) > 1:
            overview_path = self.generate_market_overview(companies, report_dir)
            generated["market_overview"] = overview_path

        logger.info(f"Generated {len(generated)} report sets in {report_dir}")
        return generated

    def generate_company_reports(self, company: Company, output_dir: Path | None = None) -> dict[str, Path]:
        """Generate all report types for a single company."""
        output_dir = output_dir or self.output_dir

        # Create company-specific directory
        company_dir = output_dir / self._sanitize_filename(company.name)
        company_dir.mkdir(parents=True, exist_ok=True)

        generated = {
            "corporate_history": self.generate_corporate_history(company, company_dir),
            "deep_analysis": self.generate_deep_analysis(company, company_dir),
            "financial_growth": self.generate_financial_growth(company, company_dir),
        }

        return generated

    def generate_corporate_history(self, company: Company, output_dir: Path) -> Path:
        """Generate corporate history report."""
        report = f"""# Corporate History - {company.name}

**Report Date**: {datetime.now().strftime("%B %Y")}
**Data Source**: SolStein Competitive Intelligence Platform
**Classification**: {company.classification or "N/A"}

---

## Executive Summary

{company.name} is a{" " if company.industry else ""}{company.industry or "energy software"} company
{"operating from " + company.headquarters if company.headquarters else ""}.
With {company.financials.employees or "N/A"} employees and €{company.financials.revenue or 0:.1f}M revenue,
the company demonstrates a {self._classify_trajectory(company)} trajectory.

**Composite Score**: {company.composite_score or "N/A"} | **Classification**: {company.classification or "N/A"}

---

## Company Profile

| Attribute | Value |
|---|---|
| Name | {company.name} |
| Industry | {company.industry or "N/A"} |
| Headquarters | {company.headquarters or "N/A"} |
| Founded | {company.founded_year or "N/A"} |
| Employees | {f"{company.financials.employees:,}" if company.financials.employees else "N/A"} |
| Revenue | €{company.financials.revenue or 0:.1f}M |
| Ownership | {"PE-backed" if company.funding_rounds else "Independent"} |
| Data Source | {company.data_source or "SolStein Intelligence"} |

---

## Financial Performance

### Revenue

| Year | Revenue | YoY Growth | Source |
|---|---|---|---|
| Current | €{company.financials.revenue or 0:.1f}M | {company.financials.growth_rate or "N/A"}% | SolStein Estimate |
| CAGR (3yr) | {company.revenue_cagr_3yr or "N/A"}% | | Calculated |

### Employees

| Metric | Value |
|---|---|
| Current Headcount | {f"{company.financials.employees:,}" if company.financials.employees else "N/A"} |
| Employee CAGR (3yr) | {company.employee_cagr_3yr or "N/A"}% |
| Open Positions | {company.open_positions or "N/A"} |

---

## Ownership & Funding

| Event | Details |
|---|---|
| Total Funding | {"€" + f"{company.total_funding_raised_eur / 1e6:.0f}M" if company.total_funding_raised_eur else "Undisclosed"} |
| Latest Valuation | {"€" + f"{company.latest_valuation_eur / 1e6:.0f}M" if company.latest_valuation_eur else "Undisclosed"} |
| Lead Investors | {", ".join(company.lead_investors) if company.lead_investors else "N/A"} |

### Funding Rounds

{self._format_funding_rounds(company.funding_rounds)}

---

## Technology & Product

### Tech Stack

{", ".join(company.tech_stack) if company.tech_stack else "Data not available"}

### SaaS Maturity

| Dimension | Score |
|---|---|
| Overall Maturity | {company.saas_maturity or "N/A"}/10 |
| AI Score | {company.ai_score or "N/A"}/10 |

---

## Market Position

### Geographic Presence

{", ".join(company.geographic_presence) if company.geographic_presence else "Data not available"}

### Key Customers

{", ".join(company.key_customers[:10]) if company.key_customers else "Data not available"}

---

## Scoring Breakdown

| Score Type | Value | Interpretation |
|---|---|---|
| Growth Score | {company.growth_score or "N/A"}/10 | {self._interpret_growth(company.growth_score)} |
| Financial Health | {company.financial_health_score or "N/A"}/10 | {self._interpret_health(company.financial_health_score)} |
| Competitive Position | {company.competitive_position_score or "N/A"}/10 | {self._interpret_position(company.competitive_position_score)} |
| **Composite** | **{company.composite_score or "N/A"}/10** | **{company.classification or "N/A"}** |

---

## Data Quality

| Field | Availability |
|---|---|
| Revenue | {"✓" if company.financials.revenue else "✗"} |
| Growth Rate | {"✓" if company.financials.growth_rate else "✗"} |
| Employees | {"✓" if company.financials.employees else "✗"} |
| Profit Margin | {"✓" if company.profit_margin else "✗"} |
| AI Score | {"✓" if company.ai_score is not None else "✗"} |
| Funding | {"✓" if company.total_funding_raised_eur else "✗"} |
| Valuation | {"✓" if company.latest_valuation_eur else "✗"} |

---

*Report generated by SolStein Competitive Intelligence Platform*
*Data as of {datetime.now().strftime("%B %Y")}*
"""
        output_path = output_dir / "corporate-history.md"
        output_path.write_text(report)
        return output_path

    def generate_deep_analysis(self, company: Company, output_dir: Path) -> Path:
        """Generate deep analysis report."""
        threat = company.threat_level.value if company.threat_level else "Unknown"
        tier = company.tier.value if company.tier else "Unknown"

        report = f"""# Deep Analysis - {company.name}

**Report Date**: {datetime.now().strftime("%B %Y")}
**Data Source**: SolStein Competitive Intelligence Platform
**Classification**: {company.classification or "N/A"}

---

## Company Fundamentals

| Data Point | Value | Confidence |
|---|---|---|
| Legal Entity | {company.name} | High |
| Industry | {company.industry or "N/A"} | High |
| Headquarters | {company.headquarters or "N/A"} | High |
| Founded | {company.founded_year or "N/A"} | Medium |
| Employees | {f"{company.financials.employees:,}" if company.financials.employees else "N/A"} | High |
| Revenue | €{company.financials.revenue or 0:.1f}M | High |
| Ownership | {"PE-backed" if company.funding_rounds else "Independent"} | High |
| Last Updated | {company.last_updated.strftime("%Y-%m-%d") if company.last_updated else "N/A"} | High |

---

## Positioning

| Dimension | Value |
|---|---|
| Tier | {tier} |
| Threat Level | {threat} |
| AI Maturity | {company.ai_maturity.value if company.ai_maturity else "N/A"} |
| SaaS Maturity | {company.saas_maturity or "N/A"}/10 |

---

## Financial Metrics

| Metric | Value | YoY Change |
|---|---|---|
| Revenue | €{company.financials.revenue or 0:.1f}M | {company.financials.growth_rate or "N/A"}% |
| Profit Margin | {company.profit_margin or "N/A"}% | N/A |
| EBITDA Margin | {company.ebitda_margin or "N/A"}% | N/A |
| Revenue per Employee | €{company.revenue_per_employee_eur_k or 0:.0f}K | N/A |
| Recurring Revenue | {company.recurring_revenue_pct or "N/A"}% | N/A |

---

## Growth Trajectory

| Metric | Value |
|---|---|
| Revenue CAGR (3yr) | {company.revenue_cagr_3yr or "N/A"}% |
| Employee CAGR (3yr) | {company.employee_cagr_3yr or "N/A"}% |
| 3-Year Revenue Growth | {self._calculate_3yr_growth(company)} |

---

## AI & Innovation

| Capability | Status |
|---|---|
| AI Score | {company.ai_score or 0}/10 |
| AI Signal | {company.ai_signal_level or "None"} |
| AI in Production | {"Yes" if company.ai_in_production else "No"} |
| Key AI Capabilities | {company.ai_key_capabilities or "None identified"} |

---

## Technology Assessment

| Dimension | Assessment |
|---|---|
| Deployment Model | {"SaaS" if company.saas_maturity and company.saas_maturity >= 5 else "Hybrid/On-premise"} |
| Tech Stack | {", ".join(company.tech_stack[:5]) if company.tech_stack else "Data not available"} |
| API Strategy | {"REST APIs available" if company.tech_stack and "API" in str(company.tech_stack) else "Data not available"} |

---

## Competitive Position

### Scoring Summary

| Dimension | Score | Max | Assessment |
|---|---|---|---|
| Growth Score | {company.growth_score or "N/A"} | 10 | {self._interpret_growth(company.growth_score)} |
| Financial Health | {company.financial_health_score or "N/A"} | 10 | {self._interpret_health(company.financial_health_score)} |
| Competitive Position | {company.competitive_position_score or "N/A"} | 10 | {self._interpret_position(company.competitive_position_score)} |
| **Composite Score** | **{company.composite_score or "N/A"}** | 10 | **{company.classification or "N/A"}** |

### Classification Criteria

- 🔥 **Phoenix** (Score ≥ 7.0): Explosive growth, market disruptor
- 🧂 **Salt** (Score 4.0-6.9): Stable, investing in future
- ⚖️ **Lead** (Score ≤ 3.9): Legacy, evolutionary

**Current Classification**: {company.classification or "N/A"}

---

## Geographic & Market

### Presence

{", ".join(company.geographic_presence) if company.geographic_presence else "Data not available"}

### Notable Customers

{", ".join(company.key_customers[:10]) if company.key_customers else "Data not available"}

---

## Strengths & Weaknesses

### Key Strengths

{self._generate_strengths(company)}

### Key Weaknesses

{self._generate_weaknesses(company)}

---

## Strategic Assessment

**Position**: {company.classification or "N/A"} ({company.composite_score or "N/A"}/10)

{self._generate_strategic_assessment(company)}

---

*Report generated by SolStein Competitive Intelligence Platform*
*Data as of {datetime.now().strftime("%B %Y")}*
"""
        output_path = output_dir / "deep-analysis.md"
        output_path.write_text(report)
        return output_path

    def generate_financial_growth(self, company: Company, output_dir: Path) -> Path:
        """Generate financial growth report."""
        report = f"""# Financial & Growth Deep-Dive - {company.name}

**Report Date**: {datetime.now().strftime("%B %Y")}
**Data Source**: SolStein Competitive Intelligence Platform

---

## Revenue Timeline

| Year | Revenue (€M) | YoY Growth | Confidence |
|---|---|---|---|
| Current | {company.financials.revenue or "N/A"} | {company.financials.growth_rate or "N/A"}% | Estimated |
| 3yr CAGR | {company.revenue_cagr_3yr or "N/A"}% | | Calculated |

---

## Profitability

| Metric | Value | Source |
|---|---|---|
| Profit Margin | {company.profit_margin or "N/A"}% | Estimated |
| EBITDA Margin | {company.ebitda_margin or "N/A"}% | Estimated |
| Recurring Revenue | {company.recurring_revenue_pct or "N/A"}% | Estimated |
| Revenue/Employee | €{company.revenue_per_employee_eur_k or 0:.0f}K | Calculated |

---

## Funding & Investment

| Event | Details |
|---|---|
| Total Raised | {"€" + f"{company.total_funding_raised_eur / 1e6:.0f}M" if company.total_funding_raised_eur else "Undisclosed"} |
| Valuation | {"€" + f"{company.latest_valuation_eur / 1e6:.0f}M" if company.latest_valuation_eur else "Undisclosed"} |
| Lead Investors | {", ".join(company.lead_investors) if company.lead_investors else "N/A"} |

{self._format_funding_detail(company.funding_rounds)}

---

## Employee Growth

| Year | Headcount | Growth |
|---|---|---|
| Current | {f"{company.financials.employees:,}" if company.financials.employees else "N/A"} | |
| CAGR (3yr) | {company.employee_cagr_3yr or "N/A"}% | |
| Open Positions | {company.open_positions or "N/A"} | |

---

## Growth Scorecard

| Dimension | Score | Assessment |
|---|---|---|
| Revenue Growth | {company.growth_score or 5:.1f}/10 | {self._interpret_growth(company.growth_score)} |
| Funding Momentum | {self._score_funding(company)}/10 | {self._interpret_funding(company)} |
| Employee Growth | {self._score_employee_growth(company)}/10 | {self._interpret_employee_growth(company)} |
| Geographic Expansion | {self._score_geographic(company)}/10 | {self._interpret_geographic(company)} |
| M&A Activity | {self._score_ma(company)}/10 | {self._interpret_ma(company)} |
| SaaS Maturity | {company.saas_maturity or 1}/10 | {self._interpret_saas(company)} |
| **Composite Score** | **{company.composite_score or 5:.1f}/10** | **{company.classification or "N/A"}** |

---

## Classification: {company.classification or "N/A"}

- 🔥 **Phoenix** (Score ≥ 7.0): Explosive growth, market disruptor
- 🧂 **Salt** (Score 4.0-6.9): Stable, investing in future
- ⚖️ **Lead** (Score ≤ 3.9): Legacy, evolutionary

---

## Data Gaps

| Data Point | Status |
|---|---|
| Exact Revenue | {"Available" if company.financials.revenue else "Estimated"} |
| Profitability | {"Available" if company.profit_margin else "Not disclosed"} |
| Funding Details | {"Available" if company.funding_rounds else "Undisclosed"} |
| Valuation | {"Available" if company.latest_valuation_eur else "Undisclosed"} |

---

*Report generated by SolStein Competitive Intelligence Platform*
*Data as of {datetime.now().strftime("%B %Y")}*
"""
        output_path = output_dir / "financial-growth.md"
        output_path.write_text(report)
        return output_path

    def generate_market_overview(self, companies: list[Company], output_dir: Path) -> Path:
        """Generate market overview report with all companies."""
        # Sort by composite score
        sorted_companies = sorted(companies, key=lambda c: c.composite_score or 0, reverse=True)

        phoenixes = [c for c in sorted_companies if c.classification == "Phoenix"]
        salts = [c for c in sorted_companies if c.classification == "Salt"]
        leads = [c for c in sorted_companies if c.classification == "Lead"]

        report = f"""# Competitive Landscape Overview

**Report Date**: {datetime.now().strftime("%B %Y")}
**Companies Analyzed**: {len(companies)}
**Data Source**: SolStein Competitive Intelligence Platform

---

## Executive Summary

This report provides a comprehensive overview of the competitive landscape,
analyzing {len(companies)} companies across multiple dimensions including
revenue growth, funding, technology maturity, and market positioning.

### Classification Distribution

| Classification | Count | Description |
|---|---|---|
| 🔥 Phoenix | {len(phoenixes)} | Explosive growth, market disruptors |
| 🧂 Salt | {len(salts)} | Stable, investing in future |
| ⚖️ Lead | {len(leads)} | Legacy, evolutionary |

---

## Revenue Leaderboard

| Rank | Company | Revenue (€M) | CAGR | Classification |
|---|---|---|---|---|
"""

        for i, c in enumerate(sorted_companies[:20], 1):
            report += f"| {i} | {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {c.classification or 'N/A'} |\n"

        report += """

## Growth Classification Matrix

### 🔥 Phoenixes (Composite Score ≥ 7.0)

| Company | Composite | Revenue | Growth | SaaS |
|---|---|---|---|---|
"""
        for c in phoenixes:
            report += f"| {c.name} | {c.composite_score or 'N/A'} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {c.saas_maturity or 'N/A'} |\n"

        report += """

### 🧂 Salts (Composite Score 4.0-6.9)

| Company | Composite | Revenue | Growth | SaaS |
|---|---|---|---|---|
"""
        for c in salts:
            report += f"| {c.name} | {c.composite_score or 'N/A'} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {c.saas_maturity or 'N/A'} |\n"

        report += """

### ⚖️ Leads (Composite Score ≤ 3.9)

| Company | Composite | Revenue | Growth | SaaS |
|---|---|---|---|---|
"""
        for c in leads[:10]:
            report += f"| {c.name} | {c.composite_score or 'N/A'} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {c.saas_maturity or 'N/A'} |\n"

        # AI Adoption Ranking
        ai_sorted = sorted(
            [c for c in companies if c.ai_score is not None],
            key=lambda c: c.ai_score or 0,
            reverse=True,
        )

        report += """

## AI Adoption Ranking

| Rank | Company | AI Score | Classification |
|---|---|---|---|
"""
        for i, c in enumerate(ai_sorted[:15], 1):
            report += f"| {i} | {c.name} | {c.ai_score}/10 | {c.classification or 'N/A'} |\n"

        report += f"""

---

## Market Statistics

| Metric | Average | Median | Max | Min |
|---|---|---|---|---|
| Revenue (€M) | {self._avg([c.financials.revenue for c in companies if c.financials.revenue]):.1f} | {self._median([c.financials.revenue for c in companies if c.financials.revenue]):.1f} | {max([c.financials.revenue or 0 for c in companies]):.1f} | {min([c.financials.revenue or float("inf") for c in companies if c.financials.revenue]):.1f} |
| Revenue CAGR | {self._avg([c.revenue_cagr_3yr for c in companies if c.revenue_cagr_3yr]):.1f}% | {self._median([c.revenue_cagr_3yr for c in companies if c.revenue_cagr_3yr]):.1f}% | {max([c.revenue_cagr_3yr or 0 for c in companies]):.1f}% | {min([c.revenue_cagr_3yr or 0 for c in companies]):.1f}% |
| Composite Score | {self._avg([c.composite_score for c in companies if c.composite_score]):.1f} | {self._median([c.composite_score for c in companies if c.composite_score]):.1f} | {max([c.composite_score or 0 for c in companies]):.1f} | {min([c.composite_score or float("inf") for c in companies if c.composite_score]):.1f} |
| AI Score | {self._avg([c.ai_score for c in companies if c.ai_score is not None]):.1f} | {self._median([c.ai_score for c in companies if c.ai_score is not None]):.1f} | {max([c.ai_score or 0 for c in companies])} | {min([c.ai_score or 0 for c in companies])} |

---

*Report generated by SolStein Competitive Intelligence Platform*
*Data as of {datetime.now().strftime("%B %Y")}*
"""
        output_path = output_dir / "market-overview.md"
        output_path.write_text(report)
        return output_path

    # Helper methods

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize company name for use as filename."""
        return name.lower().replace(" ", "-").replace("/", "-")

    def _classify_trajectory(self, company: Company) -> str:
        """Classify company trajectory based on scores."""
        score = company.composite_score or 5
        if score >= 7:
            return "high-growth"
        elif score >= 5:
            return "steady"
        else:
            return "legacy"

    def _interpret_growth(self, score: float | None) -> str:
        """Interpret growth score."""
        if score is None:
            return "No data"
        if score >= 7:
            return "Strong growth"
        elif score >= 5:
            return "Moderate growth"
        else:
            return "Weak growth"

    def _interpret_health(self, score: float | None) -> str:
        """Interpret financial health score."""
        if score is None:
            return "No data"
        if score >= 7:
            return "Strong financial position"
        elif score >= 5:
            return "Stable"
        else:
            return "Weak"

    def _interpret_position(self, score: float | None) -> str:
        """Interpret competitive position score."""
        if score is None:
            return "No data"
        if score >= 7:
            return "Strong competitive position"
        elif score >= 5:
            return "Moderate position"
        else:
            return "Weak position"

    def _calculate_3yr_growth(self, company: Company) -> str:
        """Calculate 3-year revenue growth percentage."""
        if company.revenue_cagr_3yr:
            # CAGR formula: (1 + CAGR)^3 - 1
            growth = ((1 + company.revenue_cagr_3yr / 100) ** 3 - 1) * 100
            return f"{growth:.0f}%"
        return "N/A"

    def _generate_strengths(self, company: Company) -> str:
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

    def _generate_weaknesses(self, company: Company) -> str:
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

    def _generate_strategic_assessment(self, company: Company) -> str:
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

    def _format_funding_rounds(self, funding_rounds: list) -> str:
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

    def _format_funding_detail(self, funding_rounds: list) -> str:
        """Format detailed funding information."""
        if not funding_rounds:
            return "**Funding Details**: No rounds disclosed"

        return "### Funding Rounds\n\n" + self._format_funding_rounds(funding_rounds)

    def _score_funding(self, company: Company) -> int:
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

    def _score_employee_growth(self, company: Company) -> int:
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

    def _score_geographic(self, company: Company) -> int:
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

    def _score_ma(self, company: Company) -> int:
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

    def _interpret_funding(self, company: Company) -> str:
        """Interpret funding score."""
        score = self._score_funding(company)
        if score >= 7:
            return "Strong funding backing"
        elif score >= 4:
            return "Moderate funding"
        else:
            return "Limited funding"

    def _interpret_employee_growth(self, company: Company) -> str:
        """Interpret employee growth."""
        score = self._score_employee_growth(company)
        if score >= 7:
            return "Rapid hiring"
        elif score >= 4:
            return "Steady growth"
        else:
            return "Slow hiring"

    def _interpret_geographic(self, company: Company) -> str:
        """Interpret geographic expansion."""
        score = self._score_geographic(company)
        if score >= 7:
            return "Global presence"
        elif score >= 4:
            return "Regional expansion"
        else:
            return "Limited expansion"

    def _interpret_ma(self, company: Company) -> str:
        """Interpret M&A activity."""
        score = self._score_ma(company)
        if score >= 7:
            return "Active acquirer"
        elif score >= 4:
            return "Some acquisitions"
        else:
            return "No M&A"

    def _interpret_saas(self, company: Company) -> str:
        """Interpret SaaS maturity."""
        score = company.saas_maturity or 0
        if score >= 8:
            return "Cloud-native"
        elif score >= 5:
            return "Hybrid"
        else:
            return "On-premise"

    def _avg(self, values: list) -> float:
        """Calculate average."""
        values = [v for v in values if v is not None and v != float("inf")]
        return sum(values) / len(values) if values else 0

    def _median(self, values: list) -> float:
        """Calculate median."""
        values = sorted([v for v in values if v is not None and v != float("inf")])
        if not values:
            return 0
        n = len(values)
        if n % 2 == 0:
            return (values[n // 2 - 1] + values[n // 2]) / 2
        else:
            return values[n // 2]


class ClientReportGenerator(ReportGenerator):
    """Extended report generator for client-specific reports."""

    def generate_client_report(
        self,
        client_company: Company,
        competitors: list[Company],
        output_dir: Path | None = None,
    ) -> dict[str, Path]:
        """Generate complete client report with competitive analysis."""
        output_dir = output_dir or self.output_dir / self._sanitize_filename(client_company.name)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated = {}

        # Generate individual company reports
        generated.update(self.generate_company_reports(client_company, output_dir))

        # Generate competitive analysis
        generated["competitive_analysis"] = self._generate_competitive_analysis(client_company, competitors, output_dir)

        # Generate market overview for this client's market
        generated["market_overview"] = self.generate_market_overview(competitors + [client_company], output_dir)

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

        report = f"""# Competitive Analysis - {client.name}

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
| Competitive Position | {client.competitive_position_score or "N/A"} | {_fmt_float(position_market_avg)} | {_fmt_float(position_top)} |
| Composite | {client.composite_score or "N/A"} | {_fmt_float(composite_market_avg)} | {_fmt_float(composite_top)} |

---

## Direct Competitors

These companies operate in the same tier with similar market positioning:

| Company | Revenue | CAGR | Score | Classification |
|---|---|---|---|---|
"""
        for c in direct:
            report += f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {c.composite_score or 'N/A'} | {c.classification or 'N/A'} |\n"

        report += """

## Competitive Threats

Companies with superior composite scores that could disrupt market position:

| Company | Revenue | CAGR | Score | Threat Level |
|---|---|---|---|---|
"""
        for c in threats:
            score_diff = (c.composite_score or 0) - (client.composite_score or 0)
            threat = "High" if score_diff > 2 else "Medium" if score_diff > 1 else "Low"
            report += f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {c.composite_score or 'N/A'} | {threat} |\n"

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

| Company | Revenue | CAGR | AI | SaaS | Classification |
|---|---|---|---|---|---|
"""
        for c in sorted_comp:
            report += f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.revenue_cagr_3yr or 'N/A'}% | {c.ai_score or 'N/A'} | {c.saas_maturity or 'N/A'} | {c.classification or 'N/A'} |\n"

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

        if client.ai_score is not None:
            avg_ai = self._avg([c.ai_score for c in competitors if c.ai_score is not None])
            if client.ai_score < avg_ai - 1:
                weaknesses.append(f"AI gap ({client.ai_score}/10 vs {avg_ai:.1f} market avg)")

        if client.saas_maturity:
            avg_saas = self._avg([c.saas_maturity for c in competitors if c.saas_maturity])
            if client.saas_maturity < avg_saas - 1:
                weaknesses.append(f"SaaS maturity gap ({client.saas_maturity} vs {avg_saas:.1f} avg)")

        if not client.latest_valuation_eur:
            weaknesses.append("No disclosed valuation (competitors have clearer market positioning)")

        return "\n".join([f"- {w}" for w in weaknesses]) if weaknesses else "- No significant weaknesses identified"


class LLMEnhancedReportGenerator(ClientReportGenerator):
    """Extended report generator with LLM-powered enhancements."""

    async def generate_llm_enhanced_report(
        self,
        client_company: Company,
        competitors: list[Company],
        output_dir: Path | None = None,
    ) -> dict[str, Path]:
        """Generate complete LLM-enhanced client report."""
        output_dir = output_dir or self.output_dir / self._sanitize_filename(client_company.name)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated = {}

        if self._llm_enhancer and self._llm_enhancer.is_available():
            logger.info(f"Generating LLM-enhanced reports for {client_company.name}")

            exec_summary = await self._llm_enhancer.generate_executive_summary(client_company, competitors)
            generated["executive_summary"] = self._save_llm_content("executive-summary.md", exec_summary, output_dir)

            swot = await self._llm_enhancer.generate_swot_analysis(client_company, competitors)
            swot_path = self._save_swot_report(swot, output_dir)
            generated["swot_analysis"] = swot_path

            recommendations = await self._llm_enhancer.generate_strategic_recommendations(client_company, competitors)
            rec_path = self._save_recommendations(recommendations, output_dir)
            generated["recommendations"] = rec_path

            narrative = await self._llm_enhancer.generate_competitive_narrative(client_company, competitors)
            generated["competitive_narrative"] = self._save_llm_content(
                "competitive-narrative.md", narrative, output_dir
            )

            market_insights = await self._llm_enhancer.generate_market_insights(competitors + [client_company])
            generated["market_insights"] = self._save_llm_content("market-insights.md", market_insights, output_dir)
        else:
            logger.warning("LLM not available, generating standard reports")

        generated.update(self.generate_client_report(client_company, competitors, output_dir))

        logger.info(f"Generated LLM-enhanced report for {client_company.name}")
        return generated

    def _save_llm_content(self, filename: str, content: str, output_dir: Path) -> Path:
        """Save LLM-generated content to file."""
        path = output_dir / filename
        path.write_text(content)
        return path

    def _save_swot_report(self, swot: dict, output_dir: Path) -> Path:
        """Save SWOT analysis as markdown."""
        content = """# SWOT Analysis

## Strengths

"""
        for item in swot.get("strengths", []):
            content += f"- {item}\n"

        content += """
## Weaknesses

"""
        for item in swot.get("weaknesses", []):
            content += f"- {item}\n"

        content += """
## Opportunities

"""
        for item in swot.get("opportunities", []):
            content += f"- {item}\n"

        content += """
## Threats

"""
        for item in swot.get("threats", []):
            content += f"- {item}\n"

        return self._save_llm_content("swot-analysis.md", content, output_dir)

    def _save_recommendations(self, recommendations: list, output_dir: Path) -> Path:
        """Save strategic recommendations as markdown."""
        content = """# Strategic Recommendations

"""
        for i, rec in enumerate(recommendations, 1):
            content += f"{i}. {rec}\n"

        return self._save_llm_content("recommendations.md", content, output_dir)


def generate_enhanced_report(
    company_name: str,
    use_llm: bool = True,
    output_dir: str | None = None,
) -> dict[str, Path]:
    """Convenience function to generate report for a company.

    Args:
        company_name: Name of company to analyze
        use_llm: Whether to use LLM enhancements
        output_dir: Output directory path

    Returns:
        Dict of generated report files
    """
    from ..analytics.scoring import GrowthScorer
    from ..data.loaders import CompetitorDataLoader

    loader = CompetitorDataLoader()
    companies = loader.load_companies()

    scorer = GrowthScorer()
    scored = [scorer.calculate_scores(c) for c in companies]

    target = None
    for c in scored:
        if company_name.lower() in c.name.lower():
            target = c
            break

    if not target:
        raise ValueError(f"Company not found: {company_name}")

    competitors = [c for c in scored if c.id != target.id]

    if use_llm:
        generator = LLMEnhancedReportGenerator(output_dir=Path(output_dir) if output_dir else None)
        return asyncio.run(generator.generate_llm_enhanced_report(target, competitors))
    else:
        generator = ClientReportGenerator(output_dir=Path(output_dir) if output_dir else None, use_llm=False)
        return generator.generate_client_report(target, competitors)
