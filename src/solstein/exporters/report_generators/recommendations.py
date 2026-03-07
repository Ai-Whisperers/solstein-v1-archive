"""Strategic recommendations report generator.

EPIC-022: Extracted from LLMReportEnhancer for modularity.
"""

from typing import Any

from .base import ReportGenerator, StrategicRecommendations


class RecommendationsGenerator(ReportGenerator):
    """Generate strategic recommendations reports."""

    @property
    def name(self) -> str:
        return "recommendations"

    async def generate(self, company: Any, competitors: list[Any] | None = None) -> list[str]:
        """Generate strategic recommendations.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            List of recommendation strings
        """
        company_info = self._format_company(company)
        top_threats = self._format_competitors(competitors[:5] if competitors else [], "list")

        prompt = f"""Generate 5-7 strategic recommendations for this company based on competitive analysis.

Company:
{company_info}

Top Competitors/Threats:
{top_threats}

Recommendations should be:
- Specific and actionable
- Prioritized by impact
- Considering company's current position
- Realistic given resources

Return as JSON: {{"recommendations": ["...", "..."]}}"""

        result = await self._client.generate_structured(
            prompt=prompt,
            schema=StrategicRecommendations,
        )

        if isinstance(result, StrategicRecommendations):
            return result.recommendations
        return self.fallback(company, competitors)

    def fallback(self, company: Any, competitors: list[Any] | None = None) -> list[str]:
        """Generate fallback recommendations.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            List of fallback recommendations
        """
        recs = [
            "Accelerate AI adoption to close capability gap",
            "Invest in SaaS transformation",
            "Expand geographic presence",
            "Consider strategic acquisitions",
            "Strengthen competitive positioning",
        ]
        return recs[:5]
