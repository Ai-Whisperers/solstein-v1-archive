"""SWOT analysis report generator.

EPIC-022: Extracted from LLMReportEnhancer for modularity.
"""

from typing import Any

from .base import ReportGenerator, SWOTAnalysis


class SWOTGenerator(ReportGenerator):
    """Generate SWOT analysis reports."""

    @property
    def name(self) -> str:
        return "swot_analysis"

    async def generate(self, company: Any, competitors: list[Any] | None = None) -> dict[str, list[str]]:
        """Generate SWOT analysis.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            Dict with strengths, weaknesses, opportunities, threats
        """
        company_info = self._format_company(company)
        market_context = self._format_competitors(competitors[:5] if competitors else [], "list")

        prompt = f"""Generate a detailed SWOT analysis (Strengths, Weaknesses, Opportunities, Threats) for this company.

Company:
{company_info}

Competitive Context:
{market_context}

Return as JSON with format:
{{
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "opportunities": ["...", "..."],
  "threats": ["...", "..."]
}}

Each list should have 4-6 items. Be specific and data-driven."""

        result = await self._client.generate_structured(
            prompt=prompt,
            schema=SWOTAnalysis,
        )

        if result:
            return result.model_dump()
        return self.fallback(company, competitors)

    def fallback(self, company: Any, competitors: list[Any] | None = None) -> dict[str, list[str]]:
        """Generate fallback SWOT analysis.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            Fallback SWOT dict
        """
        getattr(company, "name", "Company")
        ai_score = getattr(company, "ai_score", 0)
        growth = getattr(company, "growth_rate_pct", 0)
        revenue = getattr(company, "revenue_eur_m", 0)
        tier = getattr(company, "tier", "Unknown")

        strengths = [f"{tier}-tier market position"]
        if ai_score > 0.6:
            strengths.append(f"Strong AI capabilities (score: {ai_score:.2f})")
        if growth > 0.2:
            strengths.append(f"High growth trajectory ({growth * 100:.1f}%)")
        if revenue > 10:
            strengths.append(f"Significant revenue scale (€{revenue:.1f}M)")

        weaknesses = []
        if ai_score < 0.4:
            weaknesses.append("Limited AI adoption")
        if growth < 0.05:
            weaknesses.append("Slow growth rate")
        if not weaknesses:
            weaknesses.append("Typical operational challenges")

        opportunities = [
            "Market expansion opportunities",
            "Technology modernization",
            "Strategic partnerships",
        ]

        threats = [
            "Competitive market pressure",
            "Technology disruption risk",
        ]
        if competitors and len(competitors) > 5:
            threats.append(f"Intense competition ({len(competitors)} peers)")

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "threats": threats,
        }
