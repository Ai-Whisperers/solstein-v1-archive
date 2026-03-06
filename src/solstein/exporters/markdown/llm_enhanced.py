"""LLM-enhanced report generator.

Extracted from generator.py as part of EPIC-021 file splitting.
Generates reports with LLM-powered enhancements like executive summaries,
SWOT analysis, and strategic recommendations.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from solstein.domain.models import Company

from .client import ClientReportGenerator


class LLMEnhancedReportGenerator(ClientReportGenerator):
    """Extended report generator with LLM-powered enhancements."""

    async def generate_llm_enhanced_report(
        self,
        client_company: Company,
        competitors: list[Company],
        output_dir: Path | None = None,
    ) -> dict[str, Path]:
        """Generate complete LLM-enhanced client report."""
        output_dir = output_dir or self.output_dir / self.formatter.sanitize_filename(client_company.name)
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
