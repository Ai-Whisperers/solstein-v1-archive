"""Executive summary report generator.

EPIC-022: Extracted from LLMReportEnhancer for modularity.
"""

from typing import Any

from .base import ReportGenerator


class ExecutiveSummaryGenerator(ReportGenerator):
    """Generate executive summary reports."""

    @property
    def name(self) -> str:
        return "executive_summary"

    async def generate(self, company: Any, competitors: list[Any] | None = None) -> str:
        """Generate executive summary.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            Executive summary text
        """
        company_info = self._format_company(company)
        comp_summary = self._format_competitors(competitors[:10] if competitors else [])

        prompt = f"""Generate a concise executive summary (3-4 paragraphs) for this company analysis.

Company Profile:
{company_info}

Competitive Landscape (top competitors):
{comp_summary}

Focus on:
- Key strengths and differentiators
- Main competitive threats
- Strategic recommendations
- Growth trajectory

Write in professional, investor-ready language."""

        result = await self._client.generate(prompt=prompt)
        return result or self.fallback(company, competitors)

    def fallback(self, company: Any, competitors: list[Any] | None = None) -> str:
        """Generate fallback executive summary.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            Fallback summary text
        """
        name = getattr(company, "name", "This company")
        industry = getattr(company, "industry", "its industry")
        tier = getattr(company, "tier", "unclassified")
        revenue = getattr(company, "revenue_eur_m", 0)
        growth = getattr(company, "growth_rate_pct", 0) * 100

        summary_parts = [
            f"{name} is a {tier.lower()}-tier player in the {industry} sector.",
        ]

        if revenue > 0:
            summary_parts.append(f"With €{revenue:.1f}M in revenue")
            if growth > 0:
                summary_parts[-1] += f" and {growth:.1f}% growth"
            summary_parts[-1] += ", the company demonstrates"
            summary_parts[-1] += " strong market traction." if growth > 20 else " steady performance."

        comp_count = len(competitors) if competitors else 0
        if comp_count > 0:
            summary_parts.append(
                f"Operating in a competitive landscape with {comp_count} analyzed peers, "
                f"{name} faces typical market pressures but maintains its position."
            )

        ai_score = getattr(company, "ai_score", 0)
        if ai_score > 0.7:
            summary_parts.append("The company's strong AI capabilities position it well for future growth.")

        return " ".join(summary_parts)
