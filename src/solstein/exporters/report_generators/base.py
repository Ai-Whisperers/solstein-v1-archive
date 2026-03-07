"""Base classes for report generation strategies.

EPIC-022: Extracted from LLMReportEnhancer for modularity.
"""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class SWOTAnalysis(BaseModel):
    """SWOT analysis schema."""

    strengths: list[str] = Field(description="Key strengths")
    weaknesses: list[str] = Field(description="Key weaknesses")
    opportunities: list[str] = Field(description="Market opportunities")
    threats: list[str] = Field(description="Competitive threats")


class StrategicRecommendations(BaseModel):
    """Strategic recommendations schema."""

    recommendations: list[str] = Field(description="Specific actionable recommendations")


class ReportGenerator(ABC):
    """Base class for report generation strategies.

    Each report type (executive summary, SWOT, etc.) has its own
    generator class for modularity and testability.
    """

    def __init__(self, client: Any):
        """Initialize generator with LLM client.

        Args:
            client: Enhanced LLM client
        """
        self._client = client

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this generator."""
        pass

    @abstractmethod
    async def generate(self, company: Any, competitors: list[Any] | None = None) -> Any:
        """Generate the report.

        Args:
            company: Company domain object
            competitors: Optional list of competitor objects

        Returns:
            Generated report content
        """
        pass

    @abstractmethod
    def fallback(self, company: Any, competitors: list[Any] | None = None) -> Any:
        """Generate fallback content when LLM is unavailable.

        Args:
            company: Company domain object
            competitors: Optional list of competitor objects

        Returns:
            Fallback report content
        """
        pass

    def _format_company(self, company: Any) -> str:
        """Format company information for prompts."""
        lines = [
            f"Name: {getattr(company, 'name', 'Unknown')}",
            f"Industry: {getattr(company, 'industry', 'N/A')}",
            f"Revenue: €{getattr(company, 'revenue_eur_m', 0):.1f}M",
            f"Growth: {getattr(company, 'growth_rate_pct', 0) * 100:.1f}%",
            f"Employees: {getattr(company, 'employee_count', 0)}",
            f"AI Score: {getattr(company, 'ai_score', 0):.2f}",
            f"Tier: {getattr(company, 'tier', 'Unknown')}",
        ]
        return "\n".join(lines)

    def _format_competitors(self, competitors: list[Any], format_type: str = "list") -> str:
        """Format competitor information for prompts."""
        if not competitors:
            return "No competitors analyzed."

        if format_type == "table":
            lines = ["| Company | Revenue | Growth | AI Score | Tier |"]
            lines.append("|---------|---------|--------|----------|------|")
            for comp in competitors[:10]:
                lines.append(
                    f"| {getattr(comp, 'name', 'Unknown')} | "
                    f"€{getattr(comp, 'revenue_eur_m', 0):.1f}M | "
                    f"{getattr(comp, 'growth_rate_pct', 0) * 100:.1f}% | "
                    f"{getattr(comp, 'ai_score', 0):.2f} | "
                    f"{getattr(comp, 'tier', 'Unknown')} |"
                )
            return "\n".join(lines)
        else:
            lines = []
            for i, comp in enumerate(competitors[:10], 1):
                lines.append(
                    f"{i}. {getattr(comp, 'name', 'Unknown')} - "
                    f"{getattr(comp, 'industry', 'N/A')}, "
                    f"€{getattr(comp, 'revenue_eur_m', 0):.1f}M revenue, "
                    f"{getattr(comp, 'tier', 'Unknown')} tier"
                )
            return "\n".join(lines)
