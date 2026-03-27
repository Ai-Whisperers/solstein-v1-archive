"""Deep analysis report generator with citations and evidence integration."""

from __future__ import annotations

from datetime import datetime
from typing import Any

try:
    from solstein.evidence.models import Claim
except ImportError:
    Claim = None  # Evidence system requires Neo4j
from solstein.intelligence.capability_overlap import (
    OverlapLevel,
)
from solstein.intelligence.deep_analyzer import DeepAnalysisReport


class CitedReportGenerator:
    """Generate markdown reports with evidence citations."""

    def __init__(self):
        """Initialize report generator."""
        self.citation_counter = 0
        self.citations: dict[int, dict[str, Any]] = {}

    def generate(
        self,
        report: DeepAnalysisReport,
        claims: list[Claim] | None = None,
    ) -> str:
        """Generate complete deep analysis report with citations.

        Args:
            report: Deep analysis report with all sections
            evidence_bundle: Optional evidence bundle for citations

        Returns:
            Markdown report with citations
        """
        self.citation_counter = 0
        self.citations = {}

        sections = [
            self._generate_header(report),
            self._generate_executive_assessment(report),
            self._generate_capability_matrix(report),
            self._generate_ai_assessment(report),
            self._generate_product_offering(report),
            self._generate_strategic_implications(report),
            self._generate_blindspot_analysis(report),
            self._generate_key_insights(report),
            self._generate_citations_section(),
        ]

        return "\n\n".join(sections)

    def _generate_header(self, report: DeepAnalysisReport) -> str:
        """Generate report header."""
        company = report.company

        tier = company.tier or "Unclassified"
        classification = company.classification or "N/A"

        return f"""# Deep Analysis - {company.name}

## Executive Summary

| Attribute | Value |
|-----------|-------|
| **Company** | {company.name} |
| **Headquarters** | {company.headquarters or "Unknown"} |
| **Employees** | {company.employee_count or "Unknown"} |
| **Overall Score** | {company.composite_score or "N/A"}/10 |
| **Classification** | {classification} |
| **Tier** | {tier} |
| **Capability Overlap** | {report.capability_matrix.overall_overlap_score:.0%} |
| **Analysis Date** | {datetime.now().strftime("%Y-%m-%d")} |
"""

    def _generate_executive_assessment(self, report: DeepAnalysisReport) -> str:
        """Generate executive assessment section."""
        return f"""## Executive Assessment

{report.executive_assessment}
"""

    def _generate_capability_matrix(self, report: DeepAnalysisReport) -> str:
        """Generate capability overlap matrix section."""
        matrix = report.capability_matrix

        # Build table rows
        rows = []
        for code, match in matrix.matches.items():
            level_emoji = {
                OverlapLevel.NONE: "⚪",
                OverlapLevel.LOW: "🟡",
                OverlapLevel.MEDIUM: "🟠",
                OverlapLevel.HIGH: "🔴",
                OverlapLevel.VERY_HIGH: "🔴",
            }.get(match.overlap_level, "⚪")

            evidence_preview = ""
            if match.evidence:
                preview = match.evidence[0][:60] + "..." if len(match.evidence[0]) > 60 else match.evidence[0]
                evidence_preview = preview

            rows.append(
                f"| {level_emoji} {match.overlap_level.value.upper()} | "
                f"{code.replace('_', ' ').title()} | "
                f"{evidence_preview} |"
            )

        return f"""## Eneve Capability Overlap Matrix

**Overall Overlap Score**: {matrix.overall_overlap_score:.0%}
**Matching Capabilities**: {matrix.matching_capabilities}/8

| Overlap | Capability | Evidence |
|---------|------------|----------|
{chr(10).join(rows)}

### Strongest Matches
{chr(10).join(f"- {match}" for match in matrix.strongest_matches[:5]) or "None identified"}

### Capability Gaps
{chr(10).join(f"- {gap}" for gap in matrix.gaps[:5]) or "None identified"}
"""

    def _generate_ai_assessment(self, report: DeepAnalysisReport) -> str:
        """Generate AI assessment section."""
        ai = report.ai_assessment

        score = ai.get("score", 0)
        level = ai.get("signal_level", "LOW")

        # Signal level emoji
        emoji = {
            "VERY STRONG": "🟢",
            "STRONG": "🟢",
            "MODERATE": "🟡",
            "LOW-MODERATE": "🟠",
            "LOW": "🔴",
        }.get(level, "⚪")

        # Evidence bullets
        evidence_bullets = []
        for i, ev in enumerate(ai.get("evidence", [])[:5]):
            citation = self._add_citation(f"AI evidence {i + 1}", "source_url_placeholder")
            evidence_bullets.append(f"- {ev[:100]}{'...' if len(ev) > 100 else ''} [{citation}]")

        return f"""## AI Adoption Assessment

**Signal Level**: {emoji} {level}
**Overall Score**: {score}/10

### Signal Breakdown
{chr(10).join(f"- **{k.replace('_', ' ').title()}**: {v} occurrences" for k, v in ai.get("signal_breakdown", {}).items())}

### Key Evidence
{chr(10).join(evidence_bullets) or "No specific AI evidence identified"}
"""

    def _generate_product_offering(self, report: DeepAnalysisReport) -> str:
        """Generate product offering section."""
        return f"""## Product Offering

{report.product_offering}
"""

    def _generate_strategic_implications(self, report: DeepAnalysisReport) -> str:
        """Generate strategic implications section."""
        return f"""## Strategic Implications for Eneve

{report.strategic_implications}
"""

    def _generate_blindspot_analysis(self, report: DeepAnalysisReport) -> str:
        """Generate blindspot analysis section."""
        return f"""## Why This Competitor Is Hard to Find

{report.blindspot_analysis}
"""

    def _generate_key_insights(self, report: DeepAnalysisReport) -> str:
        """Generate key insights section."""
        insights = report.key_insights

        if not insights:
            insights = ["No specific insights identified"]

        return f"""## Key Insights

{chr(10).join(f"- {insight}" for insight in insights)}
"""

    def _generate_citations_section(self) -> str:
        """Generate citations section."""
        if not self.citations:
            return ""

        citations_text = []
        for num, data in sorted(self.citations.items()):
            citations_text.append(f"[{num}]: {data['description']}")

        return f"""---

## Sources

{chr(10).join(citations_text)}

---

*Generated by Solstein Intelligence Platform*
"""

    def _add_citation(self, description: str, source_url: str) -> int:
        """Add a citation and return citation number.

        Args:
            description: Citation description
            source_url: Source URL

        Returns:
            Citation number
        """
        self.citation_counter += 1
        self.citations[self.citation_counter] = {
            "description": description,
            "url": source_url,
        }
        return self.citation_counter


class DeepAnalysisExporter:
    """Export deep analysis reports to various formats."""

    def __init__(self):
        """Initialize exporter."""
        self.report_generator = CitedReportGenerator()

    def to_markdown(
        self,
        report: DeepAnalysisReport,
        include_citations: bool = True,
    ) -> str:
        """Export report to markdown.

        Args:
            report: Deep analysis report
            include_citations: Whether to include citations

        Returns:
            Markdown string
        """
        return self.report_generator.generate(report)

    def to_dict(self, report: DeepAnalysisReport) -> dict[str, Any]:
        """Export report to dictionary.

        Args:
            report: Deep analysis report

        Returns:
            Dictionary representation
        """
        return {
            "company": {
                "id": report.company.id,
                "name": report.company.name,
                "headquarters": report.company.headquarters,
                "employee_count": report.company.employee_count,
                "composite_score": report.company.composite_score,
                "classification": report.company.classification,
            },
            "capability_overlap": {
                "overall_score": report.capability_matrix.overall_overlap_score,
                "matching_capabilities": report.capability_matrix.matching_capabilities,
                "high_overlap_capabilities": report.capability_matrix.high_overlap_capabilities,
                "strongest_matches": report.capability_matrix.strongest_matches,
                "gaps": report.capability_matrix.gaps,
                "matches": {
                    code: {
                        "level": match.overlap_level.value,
                        "confidence": match.confidence,
                        "evidence": match.evidence,
                    }
                    for code, match in report.capability_matrix.matches.items()
                },
            },
            "ai_assessment": report.ai_assessment,
            "narrative": {
                "executive_assessment": report.executive_assessment,
                "product_offering": report.product_offering,
                "strategic_implications": report.strategic_implications,
                "blindspot_analysis": report.blindspot_analysis,
                "key_insights": report.key_insights,
            },
        }

    def generate_comparison_table(
        self,
        reports: list[DeepAnalysisReport],
    ) -> str:
        """Generate comparison table for multiple competitors.

        Args:
            reports: List of deep analysis reports

        Returns:
            Markdown comparison table
        """
        if not reports:
            return "No competitors to compare"

        # Header
        header = "| Competitor | Score | AI Signal | Overlap | Key Capabilities |"
        separator = "|---|---|---|---|---|"

        # Rows
        rows = []
        for report in reports:
            company = report.company
            ai_level = report.ai_assessment.get("signal_level", "N/A")
            overlap = f"{report.capability_matrix.overall_overlap_score:.0%}"
            key_caps = ", ".join(report.capability_matrix.strongest_matches[:2]) or "None"

            rows.append(
                f"| {company.name} | {company.composite_score or 'N/A'}/10 | {ai_level} | {overlap} | {key_caps} |"
            )

        return f"""# Competitive Comparison

{header}
{separator}
{chr(10).join(rows)}

## Summary Statistics

- **Total Competitors**: {len(reports)}
- **Average Score**: {sum(r.company.composite_score or 0 for r in reports) / len(reports):.1f}/10
- **Average Overlap**: {sum(r.capability_matrix.overall_overlap_score for r in reports) / len(reports):.0%}
"""
