"""Competitive narrative report generator.

EPIC-022: Extracted from LLMReportEnhancer for modularity.
"""

from typing import Any

from .base import ReportGenerator


class CompetitiveNarrativeGenerator(ReportGenerator):
    """Generate competitive narrative analysis reports."""

    @property
    def name(self) -> str:
        return "competitive_narrative"

    async def generate(self, company: Any, competitors: list[Any] | None = None) -> str:
        """Generate competitive narrative analysis.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            Narrative analysis text
        """
        company_info = self._format_company(company)
        all_competitors = self._format_competitors(competitors if competitors else [], "table")

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

        result = await self._client.generate(prompt=prompt)
        return result or self.fallback(company, competitors)

    def fallback(self, company: Any, competitors: list[Any] | None = None) -> str:
        """Generate fallback narrative.

        Args:
            company: Company domain object
            competitors: List of competitor objects

        Returns:
            Fallback narrative text
        """
        name = getattr(company, "name", "Company")
        classification = getattr(company, "classification", "N/A")
        industry = getattr(company, "industry", "energy software")
        revenue = getattr(company, "revenue_eur_m", 0)
        employees = getattr(company, "employee_count", "N/A")
        growth = getattr(company, "growth_rate_pct", 0) * 100
        composite = getattr(company, "composite_score", 0)
        ai_score = getattr(company, "ai_score", 0)

        return f"""## Competitive Analysis

{name} occupies a {classification} position in the {industry} market. With revenue of €{revenue:.1f}M 
and {employees} employees, the company demonstrates {growth:.1f}% year-over-year growth.

The composite score of {composite:.1f}/10 reflects {"strong" if composite > 6 else "moderate"} 
performance across growth, financial health, and competitive dimensions. The company's 
AI maturity at {ai_score:.1f}/10 represents both a challenge and opportunity 
for future development.

Competitive threats include larger players with greater resources and 
faster-growing Phoenix-class companies. Strategic priorities should focus on 
differentiating through technology investment and market expansion."""
