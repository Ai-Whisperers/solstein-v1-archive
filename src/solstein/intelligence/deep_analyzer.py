"""Deep analysis generator using LLM for narrative synthesis.

Epic 1: Deep Analysis Intelligence Module - LLM-powered report generation.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from solstein.domain.models import Company
from solstein.intelligence.capability_overlap import (
    CapabilityOverlapMatrix,
    OverlapAnalyzer,
)

# Eneve context for comparative analysis
ENEVÉ_CONTEXT = {
    "name": "Eneve",
    "product": "eBase Platform",
    "hq": "Netherlands",
    "market_position": "Market leader in Dutch energy back-office",
    "core_capabilities": [
        "Time Series Management (smart meter data)",
        "Balancing & Settlement (power allocation, imbalance)",
        "Nominations & Scheduling (TSO/DSO communication)",
        "Message Processing (EDI, validation)",
        "Market Operations (participant management)",
    ],
    "primary_markets": ["Netherlands", "Belgium"],
    "platform": "MSSQL, on-premise, migrating to C#/.NET",
}


class DeepAnalysisReport:
    """Complete deep analysis report for a competitor."""

    def __init__(
        self,
        company: Company,
        capability_matrix: CapabilityOverlapMatrix,
        ai_assessment: dict[str, Any],
    ):
        self.company = company
        self.capability_matrix = capability_matrix
        self.ai_assessment = ai_assessment

        # Report sections (populated by generator)
        self.executive_assessment: str = ""
        self.product_offering: str = ""
        self.strategic_implications: str = ""
        self.blindspot_analysis: str = ""
        self.key_insights: list[str] = []


class DeepAnalysisGenerator:
    """Generate deep analytical reports using LLM synthesis."""

    def __init__(self, llm_client=None):
        """Initialize with optional LLM client.

        Args:
            llm_client: LLM client for narrative generation. If None,
                       will use template-based generation.
        """
        self.llm_client = llm_client
        self.overlap_analyzer = OverlapAnalyzer()

    async def generate(
        self,
        company: Company,
        source_texts: list[str],
    ) -> DeepAnalysisReport:
        """Generate complete deep analysis report.

        Args:
            company: Company to analyze
            source_texts: Raw text sources (website, docs, news)

        Returns:
            DeepAnalysisReport with all sections
        """
        logger.info(
            "Generating deep analysis",
            company=company.name,
            source_count=len(source_texts),
        )

        # Step 1: Analyze capability overlap
        capability_matrix = self.overlap_analyzer.analyze(
            entity_id=company.id,
            entity_name=company.name,
            source_texts=source_texts,
        )

        # Step 2: Assess AI capabilities
        ai_assessment = self._assess_ai_capabilities(company, source_texts)

        # Step 3: Create report object
        report = DeepAnalysisReport(
            company=company,
            capability_matrix=capability_matrix,
            ai_assessment=ai_assessment,
        )

        # Step 4: Generate narrative sections
        if self.llm_client:
            await self._generate_with_llm(report, source_texts)
        else:
            self._generate_template_based(report, source_texts)

        return report

    def _assess_ai_capabilities(
        self,
        company: Company,
        source_texts: list[str],
    ) -> dict[str, Any]:
        """Assess AI capabilities from source texts.

        Args:
            company: Company to assess
            source_texts: Source texts to analyze

        Returns:
            AI assessment dictionary
        """
        combined_text = " ".join(source_texts).lower()

        # AI signal keywords by strength
        ai_signals = {
            "very_strong": [
                "ai-native",
                "machine learning",
                "deep learning",
                "neural network",
                "artificial intelligence",
                "ai platform",
                "ai-powered",
            ],
            "strong": [
                "ai",
                "ml",
                "data science",
                "predictive analytics",
                "forecasting",
                "automation",
                "algorithm",
            ],
            "moderate": [
                "analytics",
                "data-driven",
                "smart",
                "intelligent",
                "optimization",
            ],
            "low": [
                "digital",
                "software",
                "platform",
                "technology",
            ],
        }

        # Count signal occurrences
        signal_counts = {}
        total_score = 0

        for level, keywords in ai_signals.items():
            count = 0
            for keyword in keywords:
                count += combined_text.count(keyword)
            signal_counts[level] = count

            # Weight by signal strength
            weights = {
                "very_strong": 3,
                "strong": 2,
                "moderate": 1,
                "low": 0.5,
            }
            total_score += count * weights[level]

        # Normalize to 0-10 scale
        if total_score >= 50:
            ai_score = 10
            signal_level = "VERY STRONG"
        elif total_score >= 30:
            ai_score = 8
            signal_level = "STRONG"
        elif total_score >= 15:
            ai_score = 6
            signal_level = "MODERATE"
        elif total_score >= 5:
            ai_score = 4
            signal_level = "LOW-MODERATE"
        else:
            ai_score = 2
            signal_level = "LOW"

        # Extract AI evidence snippets
        evidence = []
        sentences = combined_text.split(".")
        ai_keywords = [kw for kws in ai_signals.values() for kw in kws]

        for sentence in sentences:
            for keyword in ai_keywords:
                if keyword in sentence and len(sentence.strip()) > 20:
                    evidence.append(sentence.strip())
                    break
            if len(evidence) >= 5:
                break

        return {
            "score": ai_score,
            "signal_level": signal_level,
            "total_signal_count": total_score,
            "signal_breakdown": signal_counts,
            "evidence": evidence[:5],
        }

    async def _generate_with_llm(
        self,
        report: DeepAnalysisReport,
        source_texts: list[str],
    ) -> None:
        """Generate narrative sections using LLM.

        Args:
            report: Report to populate
            source_texts: Source texts for context
        """
        if not self.llm_client:
            return

        # Prepare context for LLM
        context = self._prepare_llm_context(report, source_texts)

        # Generate each section
        try:
            report.executive_assessment = await self._llm_generate(
                prompt=self._executive_assessment_prompt(context),
                max_tokens=500,
            )

            report.product_offering = await self._llm_generate(
                prompt=self._product_offering_prompt(context),
                max_tokens=600,
            )

            report.strategic_implications = await self._llm_generate(
                prompt=self._strategic_implications_prompt(context),
                max_tokens=500,
            )

            report.blindspot_analysis = await self._llm_generate(
                prompt=self._blindspot_prompt(context),
                max_tokens=400,
            )

        except Exception as e:
            logger.error("LLM generation failed, falling back to templates", error=str(e))
            self._generate_template_based(report, source_texts)

    def _generate_template_based(
        self,
        report: DeepAnalysisReport,
        source_texts: list[str],
    ) -> None:
        """Generate narrative sections using templates (fallback).

        Args:
            report: Report to populate
            source_texts: Source texts for context
        """
        company = report.company
        matrix = report.capability_matrix
        ai = report.ai_assessment

        # Executive Assessment
        report.executive_assessment = self._template_executive_assessment(company, matrix, ai)

        # Product Offering
        report.product_offering = self._template_product_offering(company, matrix)

        # Strategic Implications
        report.strategic_implications = self._template_strategic_implications(company, matrix, ai)

        # Blindspot Analysis
        report.blindspot_analysis = self._template_blindspot_analysis(company)

        # Key Insights
        report.key_insights = self._generate_key_insights(company, matrix, ai)

    def _template_executive_assessment(
        self,
        company: Company,
        matrix: CapabilityOverlapMatrix,
        ai: dict[str, Any],
    ) -> str:
        """Generate executive assessment from template."""
        paragraphs = []

        # Opening classification
        score = company.composite_score or 0
        if score >= 8:
            classification = "market leader"
        elif score >= 6:
            classification = "strong competitor"
        elif score >= 4:
            classification = "moderate player"
        else:
            classification = "emerging or niche player"

        paragraphs.append(
            f"{company.name} is a {classification} in the energy software market "
            f"with an overall competitive score of {score:.1f}/10. "
            f"The company demonstrates {matrix.matching_capabilities} high-overlap "
            f"capabilities with Eneve's core platform."
        )

        # AI assessment
        ai_score = ai.get("score", 0)
        ai_level = ai.get("signal_level", "LOW")

        if ai_score >= 7:
            paragraphs.append(
                f"AI capabilities are a significant strength with a {ai_level} signal "
                f"({ai_score}/10). The company shows substantial AI investment and "
                f"integration across their product offering."
            )
        elif ai_score >= 4:
            paragraphs.append(
                f"AI capabilities show {ai_level.lower()} adoption ({ai_score}/10), "
                f"indicating selective implementation of AI/ML technologies."
            )
        else:
            paragraphs.append(
                f"Limited AI signal detected ({ai_score}/10), suggesting traditional "
                f"technology approaches without significant AI integration."
            )

        # Capability overlap summary
        if matrix.high_overlap_capabilities >= 5:
            paragraphs.append(
                f"This is a **direct competitor** with very high capability overlap "
                f"({matrix.high_overlap_capabilities}/8 core capabilities). "
                f"Competes directly across Eneve's core market segments."
            )
        elif matrix.high_overlap_capabilities >= 3:
            paragraphs.append(
                f"Significant capability overlap ({matrix.high_overlap_capabilities}/8) "
                f"indicates competition in key areas while maintaining differentiation "
                f"in others."
            )
        else:
            paragraphs.append(
                f"Limited capability overlap ({matrix.high_overlap_capabilities}/8) "
                f"suggests either niche focus or adjacent market positioning."
            )

        return "\n\n".join(paragraphs)

    def _template_product_offering(
        self,
        company: Company,
        matrix: CapabilityOverlapMatrix,
    ) -> str:
        """Generate product offering description from template."""
        paragraphs = []

        # Overview
        desc = company.description or f"{company.name} operates in energy software"
        paragraphs.append(desc)

        # Core capabilities
        if matrix.strongest_matches:
            caps_text = ", ".join(matrix.strongest_matches[:4])
            paragraphs.append(
                f"**Core Capabilities**: The company's strengths align with Eneve in "
                f"{caps_text}. These represent direct competitive overlap."
            )

        # Gaps
        if matrix.gaps:
            gaps_text = ", ".join(matrix.gaps[:3])
            paragraphs.append(
                f"**Differentiation**: Lower overlap in {gaps_text} suggests "
                f"potential differentiation or capability gaps relative to Eneve."
            )

        return "\n\n".join(paragraphs)

    def _template_strategic_implications(
        self,
        company: Company,
        matrix: CapabilityOverlapMatrix,
        ai: dict[str, Any],
    ) -> str:
        """Generate strategic implications from template."""
        implications = []

        # Direct threat assessment
        if matrix.overall_overlap_score >= 0.7:
            implications.append(
                f"**Direct Threat**: High capability overlap ({matrix.overall_overlap_score:.0%}) "
                f"positions {company.name} as a direct competitor for the same customers "
                f"and use cases."
            )
        elif matrix.overall_overlap_score >= 0.4:
            implications.append(
                "**Selective Competition**: Moderate overlap suggests competition in "
                "specific segments rather than head-to-head across all capabilities."
            )

        # AI threat
        ai_score = ai.get("score", 0)
        if ai_score >= 7:
            implications.append(
                f"**AI Disruption Risk**: Strong AI capabilities ({ai_score}/10) could "
                f"enable disruptive features that differentiate from Eneve's traditional approach."
            )

        # Geographic expansion
        hq = company.headquarters or "Unknown"
        if hq and "netherlands" not in hq.lower():
            implications.append(
                f"**Geographic Expansion**: Based in {hq}. If/when this company expands "
                f"to Netherlands/Belgium, direct competition with Eneve would increase."
            )

        # Market positioning
        if matrix.high_overlap_capabilities >= 5:
            implications.append(
                "**Functional Twin**: This company closely mirrors Eneve's capabilities. "
                "Watch for: pricing changes, customer wins/losses, and feature parity."
            )

        return "\n\n".join(implications) if implications else "No specific strategic implications identified."

    def _template_blindspot_analysis(self, company: Company) -> str:
        """Generate 'why we missed this' analysis from template."""
        # This would typically analyze search/positioning blindspots
        # For now, provide generic template

        reasons = [
            f"**Positioning Blindspot**: {company.name} may not position in categories "
            f"traditionally searched (e.g., 'ETRM', 'trading') even though they compete "
            f"in the same functional space.",
            "**Language/Geography**: Non-English websites or regional positioning "
            "can reduce visibility in English-language research.",
            "**Category Evolution**: The energy software market is fragmenting. "
            "New entrants may use different terminology than traditional analysts.",
        ]

        return "\n\n".join(reasons)

    def _generate_key_insights(
        self,
        company: Company,
        matrix: CapabilityOverlapMatrix,
        ai: dict[str, Any],
    ) -> list[str]:
        """Generate bullet point key insights."""
        insights = []

        # Capability insights
        if matrix.strongest_matches:
            insights.append(f"Strongest overlap in: {', '.join(matrix.strongest_matches[:2])}")

        # AI insight
        ai_level = ai.get("signal_level", "LOW")
        insights.append(f"AI signal: {ai_level} ({ai.get('score', 0)}/10)")

        # Competitive positioning
        if matrix.overall_overlap_score >= 0.7:
            insights.append("Direct competitor - monitor closely")
        elif matrix.overall_overlap_score >= 0.4:
            insights.append("Selective competitor - watch specific segments")

        # Employee context
        if company.employee_count:
            if company.employee_count > 500:
                insights.append(f"Large organization ({company.employee_count}+ employees)")
            elif company.employee_count < 50:
                insights.append(f"Small/startup ({company.employee_count} employees)")

        return insights

    def _prepare_llm_context(
        self,
        report: DeepAnalysisReport,
        source_texts: list[str],
    ) -> dict[str, Any]:
        """Prepare context dictionary for LLM prompts."""
        company = report.company
        matrix = report.capability_matrix
        ai = report.ai_assessment

        return {
            "company": {
                "name": company.name,
                "description": company.description,
                "headquarters": company.headquarters,
                "employee_count": company.employee_count,
                "website": company.website,
                "composite_score": company.composite_score,
            },
            "eneve": ENEVÉ_CONTEXT,
            "capability_overlap": {
                "overall_score": matrix.overall_overlap_score,
                "matching_capabilities": matrix.matching_capabilities,
                "strongest_matches": matrix.strongest_matches,
                "gaps": matrix.gaps,
            },
            "ai_assessment": {
                "score": ai.get("score"),
                "signal_level": ai.get("signal_level"),
                "evidence_count": len(ai.get("evidence", [])),
            },
            "source_excerpts": source_texts[:3],  # First 3 sources
        }

    async def _llm_generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using LLM client.

        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        if not self.llm_client:
            return ""

        try:
            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.strip()
        except Exception as e:
            logger.error("LLM generation error", error=str(e))
            return ""

    def _executive_assessment_prompt(self, context: dict[str, Any]) -> str:
        """Generate prompt for executive assessment section."""
        return f"""Write a 2-3 paragraph executive assessment of {context["company"]["name"]} as a competitor to Eneve.

Context:
- Company: {context["company"]["name"]} ({context["company"]["headquarters"]})
- Eneve is a Dutch energy back-office market leader with eBase platform
- Capability overlap score: {context["capability_overlap"]["overall_score"]:.0%}
- Matching capabilities: {", ".join(context["capability_overlap"]["strongest_matches"][:3])}
- AI signal: {context["ai_assessment"]["signal_level"]} ({context["ai_assessment"]["score"]}/10)

Write in professional board-level language. Highlight competitive position and key strengths/weaknesses relative to Eneve."""

    def _product_offering_prompt(self, context: dict[str, Any]) -> str:
        """Generate prompt for product offering section."""
        return f"""Write a 3-4 paragraph product offering summary for {context["company"]["name"]}.

Company Description: {context["company"]["description"] or "Energy software company"}

Key Capabilities (with Eneve overlap):
{chr(10).join(f"- {cap}" for cap in context["capability_overlap"]["strongest_matches"])}

Describe the product positioning, key features, and how it compares to Eneve's eBase platform."""

    def _strategic_implications_prompt(self, context: dict[str, Any]) -> str:
        """Generate prompt for strategic implications section."""
        return f"""Write strategic implications for Eneve regarding competitor {context["company"]["name"]}.

Competitor Context:
- HQ: {context["company"]["headquarters"]}
- Employees: {context["company"]["employee_count"]}
- Capability overlap: {context["capability_overlap"]["overall_score"]:.0%}
- AI capabilities: {context["ai_assessment"]["signal_level"]}

Explain why Eneve should care about this competitor, specific threats, and recommended actions."""

    def _blindspot_prompt(self, context: dict[str, Any]) -> str:
        """Generate prompt for blindspot analysis section."""
        return f"""Explain why {context["company"]["name"]} might be hard to discover through traditional competitive research.

Consider:
- Search term blindspots (not using obvious keywords like 'ETRM')
- Geographic/language factors
- Positioning/category differences
- Market fragmentation

Provide 2-3 specific reasons with explanations."""

    def generate_from_dict(
        self,
        company_name: str,
        company_data: dict,
    ) -> DeepAnalysisReport:
        """Generate deep analysis from raw company data (sync version).

        Args:
            company_name: Name of the company
            company_data: Dictionary with company info (basic_info, financials, etc.)

        Returns:
            DeepAnalysisReport with generated analysis sections.
        """
        basic = company_data.get("basic_info", {})
        description = basic.get("description", "")

        # Extract source texts
        source_texts = [description] if description else []
        for source in company_data.get("data_sources", []):
            if source.get("url"):
                source_texts.append(source["url"])

        # Analyze capability overlap
        capability_matrix = self.overlap_analyzer.analyze(
            entity_id=company_name.lower().replace(" ", "_"),
            entity_name=company_name,
            source_texts=source_texts if source_texts else ["energy software company"],
        )

        # Assess AI capabilities (inline simple version)
        combined_text = " ".join(source_texts).lower()
        ai_signals = {
            "very_strong": ["ai-native", "machine learning", "deep learning", "neural network", "artificial intelligence"],
            "strong": ["ai", "ml", "predictive", "automation", "algorithm"],
            "moderate": ["analytics", "data-driven", "optimization"],
        }
        signal_strength = 0
        detected_signals = []
        for level, keywords in ai_signals.items():
            for keyword in keywords:
                if keyword in combined_text:
                    detected_signals.append(keyword)
                    signal_strength += {"very_strong": 3, "strong": 2, "moderate": 1}[level]
                    break

        ai_score = min(10, signal_strength * 1.5)
        ai_assessment = {
            "score": round(ai_score, 1),
            "signal_level": "Very Strong" if ai_score >= 8 else "Strong" if ai_score >= 5 else "Moderate" if ai_score >= 2 else "Minimal",
            "evidence": detected_signals[:5],
            "evidence_count": len(detected_signals),
        }

        employees = basic.get("employees")
        if not isinstance(employees, int):
            employees = None
        founded_year = basic.get("founded_year")
        if not isinstance(founded_year, int):
            founded_year = None

        # Generate sections using templates (no LLM required)
        {
            "company": {
                "name": company_name,
                "description": description or "Energy software company",
                "headquarters": basic.get("headquarters", "Unknown"),
                "employee_count": employees if employees is not None else "Unknown",
                "website": basic.get("website", ""),
                "founded_year": founded_year,
            },
            "eneve": ENEVÉ_CONTEXT,
            "capability_overlap": {
                "overall_score": capability_matrix.overall_overlap_score,
                "matching_capabilities": capability_matrix.matching_capabilities,
                "high_overlap_capabilities": capability_matrix.high_overlap_capabilities,
                "strongest_matches": capability_matrix.strongest_matches,
                "gaps": capability_matrix.gaps,
            },
            "ai_assessment": ai_assessment,
        }

        # Generate report sections inline
        paragraphs = []
        score = capability_matrix.overall_overlap_score * 10
        if score >= 8:
            classification = "market leader"
        elif score >= 6:
            classification = "strong competitor"
        elif score >= 4:
            classification = "moderate player"
        else:
            classification = "emerging or niche player"

        paragraphs.append(
            f"{company_name} is a {classification} in the energy software market "
            f"with an overall competitive score of {score:.1f}/10. "
            f"The company demonstrates {capability_matrix.matching_capabilities} high-overlap "
            f"capabilities with Eneve's core platform."
        )

        ai_score = ai_assessment["score"]
        ai_level = ai_assessment["signal_level"]

        if ai_score >= 7:
            paragraphs.append(
                f"AI capabilities are a significant strength with a {ai_level} signal "
                f"({ai_score}/10). The company shows substantial AI investment and "
                f"integration across their product offering."
            )
        elif ai_score >= 4:
            paragraphs.append(
                f"AI capabilities show {ai_level.lower()} adoption ({ai_score}/10), "
                f"indicating selective implementation of AI/ML technologies."
            )
        else:
            paragraphs.append(
                f"Limited AI signal detected ({ai_score}/10), suggesting traditional "
                f"technology approaches without significant AI integration."
            )

        if capability_matrix.high_overlap_capabilities >= 5:
            paragraphs.append(
                f"This is a **direct competitor** with very high capability overlap "
                f"({capability_matrix.high_overlap_capabilities}/8 core capabilities). "
                f"Competes directly across Eneve's core market segments."
            )
        elif capability_matrix.high_overlap_capabilities >= 3:
            paragraphs.append(
                f"Significant capability overlap ({capability_matrix.high_overlap_capabilities}/8) "
                f"indicates competition in key areas while maintaining differentiation "
                f"in others."
            )
        else:
            paragraphs.append(
                f"Limited capability overlap ({capability_matrix.high_overlap_capabilities}/8) "
                f"suggests either niche focus or adjacent market positioning."
            )

        executive_assessment = "\n\n".join(paragraphs)

        # Product offering
        product_offering = f"## Product Overview\n\n{basic.get('description', 'Energy software company')}\n\n"
        if capability_matrix.strongest_matches:
            product_offering += "**Key Capabilities (with Eneve overlap):**\n"
            for cap in capability_matrix.strongest_matches[:5]:
                product_offering += f"- {cap}\n"

        # Strategic implications
        strategic_implications = "## Strategic Assessment\n\n"
        strategic_implications += f"**Headquarters:** {basic.get('headquarters', 'Unknown')}\n"
        strategic_implications += f"**Employees:** {basic.get('employees', 'Unknown')}\n"
        strategic_implications += f"**Founded:** {basic.get('founded_year', 'Unknown')}\n\n"
        strategic_implications += f"**Threat Level:** {'High' if capability_matrix.high_overlap_capabilities >= 5 else 'Medium' if capability_matrix.high_overlap_capabilities >= 3 else 'Low'}\n"
        strategic_implications += f"**AI Maturity:** {ai_assessment['signal_level']}\n"

        # Blindspot analysis
        blindspot_analysis = "## Why This Company Matters\n\n"
        blindspot_analysis += "This competitor may be hard to discover through traditional research because:\n\n"
        blindspot_analysis += "1. **Search term variations:** May use non-standard terminology for energy software\n"
        blindspot_analysis += "2. **Geographic factors:** Different regional positioning or market focus\n"
        blindspot_analysis += "3. **Category positioning:** Markets itself outside traditional ETRM/energy software categories\n"

        # Key insights
        key_insights = [
            f"Capability Overlap: {capability_matrix.matching_capabilities}/8 Eneve capabilities",
            f"AI Readiness: {ai_assessment['score']}/10 ({ai_assessment['signal_level']})",
            "Direct Competition: "
            + (
                "Yes"
                if capability_matrix.high_overlap_capabilities >= 5
                else "Partial" if capability_matrix.high_overlap_capabilities >= 3 else "Limited"
            ),
        ]

        company = Company(
            id=company_name.lower().replace(" ", "_"),
            name=company_name,
            company_name=company_name,
            description=description or "Energy software company",
            website=basic.get("website"),
            headquarters=basic.get("headquarters"),
            founded_year=founded_year,
            employees=employees,
            source_links=[s for s in source_texts[:5] if isinstance(s, str)],
        )

        report = DeepAnalysisReport(
            company=company,
            capability_matrix=capability_matrix,
            ai_assessment=ai_assessment,
        )
        report.executive_assessment = executive_assessment
        report.product_offering = product_offering
        report.strategic_implications = strategic_implications
        report.blindspot_analysis = blindspot_analysis
        report.key_insights = key_insights

        return report
