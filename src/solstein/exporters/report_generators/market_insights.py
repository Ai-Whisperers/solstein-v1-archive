"""Market insights report generator.

EPIC-022: Extracted from LLMReportEnhancer for modularity.
"""

from typing import Any

from .base import ReportGenerator


class MarketInsightsGenerator(ReportGenerator):
    """Generate market-wide insights reports."""

    @property
    def name(self) -> str:
        return "market_insights"

    async def generate(self, company: Any = None, competitors: list[Any] | None = None) -> str:
        """Generate market insights from multiple companies.

        Args:
            company: Not used (for interface compatibility)
            competitors: List of company objects (market data)

        Returns:
            Market insights text
        """
        companies = competitors if competitors else []
        market_summary = self._format_market_overview(companies)

        prompt = f"""Analyze this market and provide key insights:

{market_summary}

Provide:
1. Market Overview (2-3 sentences)
2. Key Trends (3-4 bullet points)
3. Investment Themes (2-3 points)
4. Risk Factors (2-3 points)

Write for institutional investors."""

        result = await self._client.generate(prompt=prompt)
        return result or self.fallback(None, companies)

    def _format_market_overview(self, companies: list[Any]) -> str:
        """Format market overview for LLM."""
        phoenixes = len([c for c in companies if getattr(c, "classification", None) == "Phoenix"])
        salts = len([c for c in companies if getattr(c, "classification", None) == "Salt"])
        leads = len([c for c in companies if getattr(c, "classification", None) == "Lead"])

        revenues = [getattr(c, "revenue_eur_m", 0) for c in companies if getattr(c, "revenue_eur_m", 0)]
        avg_revenue = sum(revenues) / len(revenues) if revenues else 0

        return f"""
Market Analysis: {len(companies)} companies
- Phoenixes: {phoenixes}, Salts: {salts}, Leads: {leads}
- Average Revenue: €{avg_revenue:.1f}M
- Total Revenue: €{sum(revenues):.1f}M
"""

    def fallback(self, company: Any = None, competitors: list[Any] | None = None) -> str:
        """Generate fallback market insights.

        Args:
            company: Not used
            competitors: List of company objects

        Returns:
            Fallback market insights text
        """
        companies = competitors if competitors else []
        return f"""## Market Insights

This market analysis covers {len(companies)} companies in the energy software sector.

**Key Observations:**
- Market shows healthy distribution across growth classifications
- AI adoption varies significantly across players
- Consolidation opportunities exist in fragmented segments

**Trends:**
- Increasing focus on AI/ML capabilities
- Shift toward SaaS delivery models
- Geographic expansion being pursued by mid-market players

**Risks:**
- Technology disruption from AI-native entrants
- Margin pressure in competitive segments
- Regulatory changes affecting market dynamics"""
