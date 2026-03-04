"""LLM-powered report enhancement module for SolStein.

Uses the enhanced LLM client with automatic health checking, smart retries,
and provider failover for reliable LLM operations.
"""

from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, Field

from ..config import get_settings
from ..llm.enhanced_client import EnhancedLLMClient, get_enhanced_llm_client

TBaseModel = TypeVar("TBaseModel", bound=BaseModel)


class SWOTAnalysis(BaseModel):
    """SWOT analysis schema."""

    strengths: list[str] = Field(description="Key strengths")
    weaknesses: list[str] = Field(description="Key weaknesses")
    opportunities: list[str] = Field(description="Market opportunities")
    threats: list[str] = Field(description="Competitive threats")


class StrategicRecommendations(BaseModel):
    """Strategic recommendations schema."""

    recommendations: list[str] = Field(description="Specific actionable recommendations")


class LLMReportEnhancer:
    """Enhance reports with LLM-generated insights.

    Uses the EnhancedLLMClient which provides:
    - Proactive health checking
    - Automatic provider failover
    - Smart retry with exponential backoff
    - Rate limit detection and handling

    Supports multiple backends:
    1. Ollama (local) - preferred
    2. OpenAI API
    3. Groq API
    4. Fireworks API

    Example:
        >>> enhancer = LLMReportEnhancer()
        >>> summary = await enhancer.generate_executive_summary(company, competitors)
        >>> print(summary)
        "Executive summary text..."
    """

    def __init__(self, enhanced_client: EnhancedLLMClient | None = None):
        """Initialize report enhancer.

        Args:
            enhanced_client: Optional pre-configured enhanced client.
                           Creates new instance if not provided.
        """
        self.settings = get_settings()
        self._client = enhanced_client or get_enhanced_llm_client()

    def is_available(self) -> bool:
        """Check if any LLM backend is available."""
        # Run async check synchronously for compatibility
        import asyncio

        try:
            health = asyncio.get_event_loop().run_until_complete(self._client.check_all_providers())
            return len(health.get("available", [])) > 0
        except Exception:
            # Fallback to settings check
            return bool(self.settings.openai_api_key or self.settings.groq_api_key or self.settings.fireworks_api_key)

    async def generate_executive_summary(self, company: Any, competitors: list[Any]) -> str:
        """Generate LLM-powered executive summary.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            Executive summary text (LLM-generated or fallback template)
        """
        company_info = self._format_company(company)
        comp_summary = self._format_competitors(competitors[:10])

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

        result = await self._client.generate(
            prompt=prompt,
            preferred_provider=self._get_preferred_provider(),
        )
        return result or self._fallback_summary(company)

    async def generate_swot_analysis(self, company: Any, competitors: list[Any]) -> dict[str, list[str]]:
        """Generate LLM-powered SWOT analysis.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            Dict with strengths, weaknesses, opportunities, threats lists
        """
        company_info = self._format_company(company)
        market_context = self._format_competitors(competitors[:5])

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
            preferred_provider=self._get_preferred_provider(),
        )

        if result:
            return result.model_dump()
        return self._fallback_swot(company)

    async def generate_strategic_recommendations(self, company: Any, competitors: list[Any]) -> list[str]:
        """Generate strategic recommendations based on competitive analysis.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            List of recommendation strings
        """
        company_info = self._format_company(company)
        top_threats = self._format_competitors(competitors[:5], format="brief")

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
            preferred_provider=self._get_preferred_provider(),
        )

        if isinstance(result, StrategicRecommendations):
            return result.recommendations
        return self._fallback_recommendations(company)

    async def generate_competitive_narrative(self, company: Any, competitors: list[Any]) -> str:
        """Generate a narrative competitive analysis.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            Narrative analysis text
        """
        company_info = self._format_company(company)
        all_competitors = self._format_competitors(competitors, format="table")

        prompt = f"""Write a competitive analysis narrative (400-600 words) for this company.

Company Profile:
{company_info}

All Competitors:
{all_competitors}

Structure:
1. Market Position - where does company fit
2. Competitive Landscape - key players and their strengths
3. Company's Competitive Advantages
4. Main Threats and Gaps
5. Strategic Outlook

Write in professional business language."""

        result = await self._client.generate(
            prompt=prompt,
            preferred_provider=self._get_preferred_provider(),
        )
        return result or self._fallback_narrative(company)

    async def generate_market_insights(self, companies: list[Any]) -> str:
        """Generate market-wide insights from multiple companies.

        Args:
            companies: List of company objects

        Returns:
            Market insights text
        """
        market_summary = self._format_market_overview(companies)

        prompt = f"""Analyze this market and provide key insights:

{market_summary}

Provide:
1. Market Overview (2-3 sentences)
2. Key Trends (3-4 bullet points)
3. Investment Themes (2-3 points)
4. Risk Factors (2-3 points)

Write for institutional investors."""

        result = await self._client.generate(
            prompt=prompt,
            preferred_provider=self._get_preferred_provider(),
        )
        return result or self._fallback_market_insights(companies)

    def _get_preferred_provider(self) -> str | None:
        """Get preferred provider from settings."""
        provider = (self.settings.llm_provider or "auto").strip().lower()
        if provider in {"auto", "none"}:
            return None
        return provider

    def _format_company(self, company: Any) -> str:
        """Format company for LLM prompt."""
        return f"""
Company: {company.name}
Industry: {company.industry or "N/A"}
Revenue: €{company.financials.revenue or 0:.1f}M
Growth: {company.financials.growth_rate or "N/A"}%
CAGR: {company.revenue_cagr_3yr or "N/A"}%
Employees: {company.financials.employees or "N/A"}
Classification: {company.classification or "N/A"}
Composite Score: {company.composite_score or "N/A"}/10
AI Score: {company.ai_score or 0}/10
SaaS Maturity: {company.saas_maturity or "N/A"}/10
Threat Level: {company.threat_level.value if company.threat_level else "N/A"}
"""

    def _format_competitors(self, competitors: list, format: str = "list") -> str:
        """Format competitors for LLM prompt."""
        if format == "brief":
            lines = []
            for c in competitors:
                lines.append(
                    f"- {c.name}: €{c.financials.revenue or 0:.1f}M revenue, {c.composite_score or 'N/A'}/10 score, {c.classification or 'N/A'}"
                )
            return "\n".join(lines)

        if format == "table":
            lines = [
                "| Company | Revenue | Score | Classification |",
                "|---|---|---|---|",
            ]
            for c in competitors:
                lines.append(
                    f"| {c.name} | €{c.financials.revenue or 0:.1f}M | {c.composite_score or 'N/A'} | {c.classification or 'N/A'} |"
                )
            return "\n".join(lines)

        lines = []
        for c in competitors:
            lines.append(
                f"- {c.name}: €{c.financials.revenue or 0:.1f}M, CAGR {c.revenue_cagr_3yr or 'N/A'}%, Score {c.composite_score or 'N/A'}, {c.classification or 'N/A'}"
            )
        return "\n".join(lines)

    def _format_market_overview(self, companies: list) -> str:
        """Format market overview for LLM."""
        phoenixes = len([c for c in companies if c.classification == "Phoenix"])
        salts = len([c for c in companies if c.classification == "Salt"])
        leads = len([c for c in companies if c.classification == "Lead"])

        revenues = [c.financials.revenue for c in companies if c.financials.revenue]
        avg_revenue = sum(revenues) / len(revenues) if revenues else 0

        return f"""
Market Analysis: {len(companies)} companies
- Phoenixes: {phoenixes}, Salts: {salts}, Leads: {leads}
- Average Revenue: €{avg_revenue:.1f}M
- Total Revenue: €{sum(revenues):.1f}M
"""

    def _fallback_summary(self, company: Any) -> str:
        """Fallback when LLM unavailable."""
        return f"""## Executive Summary

{company.name} operates in the {company.industry or "energy software"} sector with 
€{company.financials.revenue or 0:.1f}M revenue and {company.financials.employees or "N/A"} employees. 
The company demonstrates {company.classification or "N/A"} characteristics with a composite 
score of {company.composite_score or "N/A"}/10.

Key metrics show {company.financials.growth_rate or "N/A"}% growth rate and 
{company.revenue_cagr_3yr or "N/A"}% three-year CAGR. The AI score of {company.ai_score or 0}/10 
indicates {"limited" if company.ai_score and company.ai_score < 3 else "moderate"} AI adoption.

Strategic focus areas should include accelerating digital transformation and 
expanding market presence in adjacent segments."""

    def _fallback_swot(self, company: Any) -> dict:
        """Fallback SWOT when LLM unavailable."""
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []

        if company.financials.revenue and company.financials.revenue > 20:
            strengths.append(f"Solid revenue scale: €{company.financials.revenue:.1f}M")

        if company.revenue_cagr_3yr and company.revenue_cagr_3yr > 20:
            strengths.append(f"Strong growth trajectory: {company.revenue_cagr_3yr}% CAGR")

        if company.ai_score is not None and company.ai_score < 3:
            weaknesses.append(f"Limited AI capabilities: {company.ai_score}/10")

        if company.saas_maturity and company.saas_maturity < 5:
            weaknesses.append(f"Low SaaS maturity: {company.saas_maturity}/10")

        opportunities.append("Market expansion opportunities")
        opportunities.append("Potential AI adoption")
        opportunities.append("Geographic diversification")

        threats.append("Competitive pressure from Phoenix-class companies")
        threats.append("Technology disruption")

        return {
            "strengths": strengths or ["Revenue growth momentum"],
            "weaknesses": weaknesses or ["AI adoption gap"],
            "opportunities": opportunities,
            "threats": threats,
        }

    def _fallback_recommendations(self, company: Any) -> list[str]:
        """Fallback recommendations when LLM unavailable."""
        recs = [
            "Accelerate AI adoption to close capability gap",
            "Invest in SaaS transformation",
            "Expand geographic presence",
            "Consider strategic acquisitions",
            "Strengthen competitive positioning",
        ]
        return recs[:5]

    def _fallback_narrative(self, company: Any) -> str:
        """Fallback narrative when LLM unavailable."""
        return f"""## Competitive Analysis

{company.name} occupies a {company.classification or "N/A"} position in the 
{company.industry or "energy software"} market. With revenue of €{company.financials.revenue or 0:.1f}M 
and {company.financials.employees or "N/A"} employees, the company demonstrates 
{company.financials.growth_rate or "N/A"}% year-over-year growth.

The composite score of {company.composite_score or "N/A"}/10 reflects {"strong" if company.composite_score and company.composite_score > 6 else "moderate"} 
performance across growth, financial health, and competitive dimensions. The company's 
AI maturity at {company.ai_score or 0}/10 represents both a challenge and opportunity 
for future development.

Competitive threats include larger players with greater resources and 
faster-growing Phoenix-class companies. Strategic priorities should focus on 
differentiating through technology investment and market expansion."""

    def _fallback_market_insights(self, companies: list) -> str:
        """Fallback market insights when LLM unavailable."""
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


# Backward compatibility - maintain existing module interface
llm_enhancer = LLMReportEnhancer()
