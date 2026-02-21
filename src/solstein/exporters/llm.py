"""LLM-powered report enhancement module for SolStein."""

import os
from typing import Any, Optional

from loguru import logger

from ..config import get_settings


class LLMReportEnhancer:
    """Enhance reports with LLM-generated insights.

    Supports multiple backends:
    1. Ollama (local) - preferred
    2. OpenAI API
    3. Groq API
    4. Fireworks API
    """

    def __init__(self):
        settings = get_settings()
        self.groq_api_key = settings.groq_api_key
        self.openai_api_key = settings.openai_api_key
        self.fireworks_api_key = settings.fireworks_api_key
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.2:latest")
        self._client = None
        self._use_ollama = None

    def is_available(self) -> bool:
        """Check if any LLM backend is available."""
        if self._check_ollama():
            return True
        if self._has_valid_api_key():
            return True
        return False

    def _check_ollama(self) -> bool:
        if self._use_ollama is not None:
            return self._use_ollama
        try:
            import requests

            r = requests.get(f"{self.ollama_url}/api/version", timeout=2)
            self._use_ollama = r.status_code == 200
        except Exception:
            self._use_ollama = False
        return self._use_ollama

    def _has_valid_api_key(self) -> bool:
        return bool(self.groq_api_key or self.openai_api_key or self.fireworks_api_key)

    async def generate_executive_summary(
        self, company: Any, competitors: list[Any]
    ) -> str:
        """Generate LLM-powered executive summary."""
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

        result = await self._generate(prompt)
        return result or self._fallback_summary(company)

    async def generate_swot_analysis(
        self, company: Any, competitors: list[Any]
    ) -> dict[str, list[str]]:
        """Generate LLM-powered SWOT analysis."""
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

        result = await self._generate_json(prompt)
        if result:
            return result
        return self._fallback_swot(company)

    async def generate_strategic_recommendations(
        self, company: Any, competitors: list[Any]
    ) -> list[str]:
        """Generate strategic recommendations based on competitive analysis."""
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

        result = await self._generate_json(prompt)
        if result and "recommendations" in result:
            return result["recommendations"]
        return self._fallback_recommendations(company)

    async def generate_competitive_narrative(
        self, company: Any, competitors: list[Any]
    ) -> str:
        """Generate a narrative competitive analysis."""
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

        result = await self._generate(prompt)
        return result or self._fallback_narrative(company)

    async def generate_market_insights(self, companies: list[Any]) -> str:
        """Generate market-wide insights from multiple companies."""
        market_summary = self._format_market_overview(companies)

        prompt = f"""Analyze this market and provide key insights:

{market_summary}

Provide:
1. Market Overview (2-3 sentences)
2. Key Trends (3-4 bullet points)
3. Investment Themes (2-3 points)
4. Risk Factors (2-3 points)

Write for institutional investors."""

        result = await self._generate(prompt)
        return result or self._fallback_market_insights(companies)

    async def _generate(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Generate text using available LLM backend."""
        if self._check_ollama():
            return await self._query_ollama(prompt, system_prompt)
        if self._has_valid_api_key():
            return await self._query_api(prompt, system_prompt)
        return None

    async def _generate_json(self, prompt: str) -> Optional[dict]:
        """Generate JSON using available LLM backend."""
        json_prompt = f"{prompt}\n\nIMPORTANT: Response must be valid JSON only, no markdown formatting."

        result = await self._generate(json_prompt)
        if result:
            try:
                import json

                return json.loads(result)
            except json.JSONDecodeError:
                pass
        return None

    async def _query_ollama(
        self, prompt: str, system_prompt: str = None
    ) -> Optional[str]:
        """Query local Ollama instance."""
        try:
            import aiohttp

            system = (
                system_prompt
                or "You are an expert business analyst specializing in technology companies and private equity. Provide concise, data-driven insights."
            )

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.ollama_model,
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": prompt},
                        ],
                        "stream": False,
                        "options": {"temperature": 0.3},
                    },
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.warning(f"Ollama query failed: {e}")
        return None

    async def _query_api(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Query cloud LLM API."""
        try:
            client = self._get_client()
            if not client:
                return None

            system = (
                system_prompt
                or "You are an expert business analyst specializing in technology companies and private equity. Provide concise, data-driven insights."
            )

            if hasattr(client, "chat"):
                response = await client.chat.completions.create(
                    model="llama-3.1-70b-instruct",
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.warning(f"API query failed: {e}")
        return None

    def _get_client(self):
        """Get API client."""
        if self._client:
            return self._client

        if self.fireworks_api_key:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(
                    api_key=self.fireworks_api_key,
                    base_url="https://api.fireworks.ai/inference/v1",
                )
            except ImportError:
                pass

        elif self.openai_api_key:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self.openai_api_key)
            except ImportError:
                pass

        elif self.groq_api_key:
            try:
                from groq import AsyncGroq

                self._client = AsyncGroq(api_key=self.groq_api_key)
            except ImportError:
                pass

        return self._client

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
        rockets = len([c for c in companies if c.classification == "Rocket"])
        risers = len([c for c in companies if c.classification == "Rearer"])
        steadys = len([c for c in companies if c.classification == "Steady"])
        dinosaurs = len([c for c in companies if c.classification == "Dinosaur"])

        revenues = [c.financials.revenue for c in companies if c.financials.revenue]
        avg_revenue = sum(revenues) / len(revenues) if revenues else 0

        return f"""
Market Analysis: {len(companies)} companies
- Rockets: {rockets}, Risers: {risers}, Steadys: {steadys}, Dinosaurs: {dinosaurs}
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
            strengths.append(
                f"Strong growth trajectory: {company.revenue_cagr_3yr}% CAGR"
            )

        if company.ai_score is not None and company.ai_score < 3:
            weaknesses.append(f"Limited AI capabilities: {company.ai_score}/10")

        if company.saas_maturity and company.saas_maturity < 5:
            weaknesses.append(f"Low SaaS maturity: {company.saas_maturity}/10")

        opportunities.append("Market expansion opportunities")
        opportunities.append("Potential AI adoption")
        opportunities.append("Geographic diversification")

        threats.append("Competitive pressure from Rocket-class companies")
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
faster-growing Rocket-class companies. Strategic priorities should focus on 
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
