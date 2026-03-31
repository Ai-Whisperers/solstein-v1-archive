"""AI Assessment report generator for Epic 6."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from solstein.intelligence.ai_assessment_engine import (
    AIAssessment,
    AISignalLevel,
)


class AIAssessmentReportGenerator:
    """Generate markdown reports for AI capability assessments."""

    def __init__(self):
        """Initialize report generator."""
        self.citation_counter = 0
        self.citations: dict[int, dict[str, Any]] = {}

    def generate(self, assessment: AIAssessment) -> str:
        """Generate complete AI assessment report.

        Args:
            assessment: AI assessment data

        Returns:
            Markdown report
        """
        self.citation_counter = 0
        self.citations = {}

        sections = [
            self._generate_header(assessment),
            self._generate_executive_summary(assessment),
            self._generate_signal_assessment(assessment),
            self._generate_capabilities_breakdown(assessment),
            self._generate_use_cases(assessment),
            self._generate_competitive_position(assessment),
            self._generate_maturity_narrative(assessment),
            self._generate_gaps_analysis(assessment),
            self._generate_recommendations(assessment),
            self._generate_methodology_note(),
        ]

        return "\n\n".join(sections)

    def _generate_header(self, assessment: AIAssessment) -> str:
        """Generate report header."""
        signal_emoji = {
            AISignalLevel.NATIVE: "🧠",
            AISignalLevel.ADOPTED: "🤖",
            AISignalLevel.EXPERIMENTAL: "🔬",
            AISignalLevel.ABSENT: "⚪",
        }.get(assessment.signal_level, "⚪")

        confidence_color = {
            "high": "🟢",
            "medium": "🟡",
            "low": "🟠",
            "insufficient": "🔴",
        }.get(assessment.evidence_quality, "⚪")

        return f"""# AI-Native Assessment: {assessment.company_name}

## Executive Overview

| Attribute | Value |
|-----------|-------|
| **Company** | {assessment.company_name} |
| **AI Signal Level** | {signal_emoji} {assessment.signal_level.value.upper()} |
| **Overall Score** | {assessment.overall_score}/10 |
| **AI-Native Score** | {assessment.ai_native_score}/10 |
| **AI Adoption Score** | {assessment.ai_adoption_score}/10 |
| **Evidence Quality** | {confidence_color} {assessment.evidence_quality.upper()} |
| **Analysis Date** | {datetime.now().strftime("%Y-%m-%d")} |
"""

    def _generate_executive_summary(self, assessment: AIAssessment) -> str:
        """Generate executive summary section."""
        signal_desc = {
            AISignalLevel.NATIVE: "AI-native company with machine learning at its architectural core",
            AISignalLevel.ADOPTED: "Strong AI adoption with production-grade capabilities integrated into operations",
            AISignalLevel.EXPERIMENTAL: "Experimental AI usage without strategic integration",
            AISignalLevel.ABSENT: "Limited or no AI capabilities detected",
        }.get(assessment.signal_level, "Unknown AI maturity")

        verdict = {
            AISignalLevel.NATIVE: "**Strategic Priority**: High — AI-native architecture provides sustainable advantage",
            AISignalLevel.ADOPTED: "**Strategic Priority**: Medium-High — Strong AI adoption creates differentiation",
            AISignalLevel.EXPERIMENTAL: "**Strategic Priority**: Medium — Early-stage AI suggests growth potential",
            AISignalLevel.ABSENT: "**Strategic Priority**: Low — Absence of AI creates competitive risk",
        }.get(assessment.signal_level, "**Strategic Priority**: Undetermined")

        return f"""## Executive Summary

{assessment.company_name} is classified as **{signal_desc}**.

{verdict}

**Key Findings:**
- Overall AI maturity score: **{assessment.overall_score}/10**
- Detected capabilities: **{len(assessment.capabilities)}** distinct AI domains
- Primary competitive advantage: {assessment.competitive_advantage}

**Evidence Quality Note**: This assessment is based on {assessment.evidence_quality} evidence from publicly available sources. Confidence increases with data richness.
"""

    def _generate_signal_assessment(self, assessment: AIAssessment) -> str:
        """Generate AI signal level assessment."""
        signal_details = {
            AISignalLevel.NATIVE: {
                "description": "AI-Native companies have machine learning embedded in their core architecture from inception. These companies often identify as 'AI-first' or 'ML-powered' platforms.",
                "indicators": "Strong ML terminology, AI-focused positioning, dedicated ML engineering teams, proprietary algorithms",
                "examples": "Companies like DeepMind, OpenAI, or specialized ML infrastructure providers",
            },
            AISignalLevel.ADOPTED: {
                "description": "AI-Adopted companies have successfully integrated artificial intelligence into their operations, often with production-grade systems delivering measurable value.",
                "indicators": "Predictive analytics, intelligent automation, NLP applications, optimization systems",
                "examples": "Traditional software companies with strong AI/ML product features",
            },
            AISignalLevel.EXPERIMENTAL: {
                "description": "Experimental AI usage indicates early-stage exploration without full strategic integration or production deployment.",
                "indicators": "Limited AI terminology, basic analytics, proof-of-concept mentions",
                "examples": "Companies testing AI but not yet integrated into core products",
            },
            AISignalLevel.ABSENT: {
                "description": "No significant AI signals detected in publicly available information.",
                "indicators": "No AI/ML terminology, traditional software approaches, manual processes",
                "examples": "Legacy software vendors without AI transformation",
            },
        }.get(assessment.signal_level, {})

        return f"""## AI Signal Assessment

### Signal Classification: {assessment.signal_level.value.upper()}

{signal_details.get("description", "")}

**Typical Indicators:**
{signal_details.get("indicators", "N/A")}

**Score Breakdown:**
| Metric | Score | Weight | Contribution |
|--------|-------|--------|--------------|
| AI-Native Score | {assessment.ai_native_score}/10 | 60% | {assessment.ai_native_score * 0.6:.1f} |
| AI Adoption Score | {assessment.ai_adoption_score}/10 | 40% | {assessment.ai_adoption_score * 0.4:.1f} |
| **Overall Score** | | | **{assessment.overall_score}/10** |
"""

    def _generate_capabilities_breakdown(self, assessment: AIAssessment) -> str:
        """Generate detailed capabilities breakdown."""
        if not assessment.capabilities:
            return """## AI Capabilities Breakdown

**No AI capabilities detected** in available data sources.

This may indicate:
- Limited public information about the company's technology stack
- Traditional software approaches without AI integration
- Early-stage company without mature AI capabilities
"""

        rows = []
        for cap in assessment.capabilities:
            level_emoji = {
                AISignalLevel.NATIVE: "🟢",
                AISignalLevel.ADOPTED: "🟡",
                AISignalLevel.EXPERIMENTAL: "🟠",
                AISignalLevel.ABSENT: "⚪",
            }.get(cap.signal_level, "⚪")

            cap_name = cap.capability_type.value.replace("_", " ").title()
            confidence_pct = int(cap.confidence * 100)

            rows.append(f"| {level_emoji} | {cap_name} | {cap.signal_level.value.upper()} | {confidence_pct}% |")

        capability_details = []
        for cap in assessment.capabilities[:3]:
            cap_name = cap.capability_type.value.replace("_", " ").title()
            evidence_text = "\n".join(f"  - {e[:100]}..." for e in cap.evidence[:2])
            use_cases = ", ".join(cap.use_cases[:3]) if cap.use_cases else "General application"

            capability_details.append(
                f"""### {cap_name}

**Signal Level**: {cap.signal_level.value.upper()}
**Confidence**: {int(cap.confidence * 100)}%

**Detected Use Cases**:
{use_cases}

**Evidence**:
{evidence_text}
"""
            )

        return f"""## AI Capabilities Breakdown

### Detected Capabilities Summary

| Status | Capability | Level | Confidence |
|--------|------------|-------|------------|
{chr(10).join(rows)}

### Detailed Capability Analysis

{chr(10).join(capability_details)}
"""

    def _generate_use_cases(self, assessment: AIAssessment) -> str:
        """Generate identified use cases section."""
        if not assessment.primary_use_cases:
            return """## Primary AI Use Cases

**No specific use cases identified** from available data.

This suggests either limited AI deployment or lack of public documentation about AI applications.
"""

        use_case_details = []
        for use_case in assessment.primary_use_cases:
            use_case_details.append(f"- **{use_case.title()}** — Energy sector application")

        return f"""## Primary AI Use Cases

The following AI applications have been identified for {assessment.company_name}:

{chr(10).join(use_case_details)}

### Use Case Categories

**Energy-Specific Applications:**
- **Trading & Markets**: Algorithmic trading, price optimization, bid strategies
- **Grid Operations**: Demand response, load forecasting, renewable integration
- **Asset Management**: Predictive maintenance, condition monitoring, asset optimization
- **Customer Engagement**: Personalization, recommendation systems, automated support
"""

    def _generate_competitive_position(self, assessment: AIAssessment) -> str:
        """Generate competitive position analysis."""
        return f"""## Competitive Position Analysis

### AI-Driven Competitive Advantage

{assessment.competitive_advantage}

### Positioning Assessment

| Dimension | Rating | Notes |
|-----------|--------|-------|
| **AI Maturity** | {assessment.signal_level.value.upper()} | Based on signal strength and capability diversity |
| **Technical Sophistication** | {self._rating_from_score(assessment.overall_score)} | Overall AI capability score |
| **Differentiation Potential** | {self._rating_from_score(assessment.ai_native_score)} | Native AI creates stronger moats |
| **Execution Evidence** | {assessment.evidence_quality.upper()} | Quality of publicly available evidence |

### Strategic Implications

**For Investment Consideration:**
- AI-native companies command valuation premiums due to scalability advantages
- Strong AI adoption indicates operational maturity and technical competence
- Experimental AI suggests potential for rapid capability expansion
- Absence of AI may indicate disruption risk from AI-enabled competitors
"""

    def _generate_maturity_narrative(self, assessment: AIAssessment) -> str:
        """Generate maturity narrative section."""
        return f"""## AI Maturity Narrative

{assessment.ai_maturity_narrative}

### Maturity Progression Path

Based on current assessment, {assessment.company_name} sits at the **{assessment.signal_level.value.upper()}** stage of AI maturity:

```
ABSENT → EXPERIMENTAL → ADOPTED → NATIVE
   ⚪        🔬            🤖         🧠
   ↑          ↑             ↑          ↑
No AI    Testing      Production   Core
         Phase        Systems      Architecture
```

**Next Stage Requirements:**
{self._next_stage_requirements(assessment)}
"""

    def _generate_gaps_analysis(self, assessment: AIAssessment) -> str:
        """Generate gaps analysis section."""
        if not assessment.gaps:
            return """## Capability Gap Analysis

**No significant gaps identified** — company demonstrates broad AI capability coverage.

This suggests either:
- Comprehensive AI strategy with diverse capability investments
- Well-rounded technical team with multiple AI specializations
- Mature AI organization with established practices
"""

        gap_items = [f"- {gap}" for gap in assessment.gaps]

        return f"""## Capability Gap Analysis

### Undetected Capabilities

The following AI capability areas were **not detected** in available data sources:

{chr(10).join(gap_items)}

### Gap Interpretation

**Possible Explanations:**
1. **Strategic Focus**: Company may prioritize specific AI domains over others
2. **Early Stage**: Capabilities may be in development but not yet publicly documented
3. **Resource Constraints**: Limited engineering bandwidth for broad AI investment
4. **Market Position**: Core value proposition may not require certain AI capabilities

**Risk Assessment:**
{self._gap_risk_assessment(assessment)}
"""

    def _generate_recommendations(self, assessment: AIAssessment) -> str:
        """Generate strategic recommendations section."""
        if not assessment.recommendations:
            return """## Strategic Recommendations

**No specific recommendations** — maintain current AI strategy and continue monitoring competitive landscape.
"""

        rec_items = [f"{i + 1}. **{rec}**" for i, rec in enumerate(assessment.recommendations)]

        additional_recs = []
        if assessment.signal_level == AISignalLevel.NATIVE:
            additional_recs = [
                "- Consider M&A opportunities to expand AI-native technology portfolio",
                "- Evaluate partnership potential for market expansion",
                "- Monitor for talent retention risks in competitive AI talent market",
            ]
        elif assessment.signal_level == AISignalLevel.ADOPTED:
            additional_recs = [
                "- Assess potential for deeper AI integration through acquisition",
                "- Evaluate competitive moat sustainability versus AI-native competitors",
                "- Consider AI R&D investment levels relative to industry benchmarks",
            ]
        elif assessment.signal_level == AISignalLevel.EXPERIMENTAL:
            additional_recs = [
                "- Evaluate AI strategy maturity and executive commitment",
                "- Assess data infrastructure readiness for scaled AI deployment",
                "- Consider value-add from AI capability acceleration",
            ]
        else:
            additional_recs = [
                "- Evaluate AI disruption risk in the company's market segment",
                "- Consider whether AI transformation is viable or necessary",
                "- Assess competitive positioning versus AI-enabled competitors",
            ]

        return f"""## Strategic Recommendations

### For Investment Consideration

{chr(10).join(rec_items)}

### Additional Strategic Considerations

{chr(10).join(additional_recs)}

### Monitoring Priorities

**Key Signals to Watch:**
- AI/ML engineering job postings (indicates investment direction)
- Partnership announcements with AI vendors or research institutions
- Product releases featuring AI-powered capabilities
- Patent filings related to machine learning or AI applications
- Conference presentations or technical blog posts on AI topics
"""

    def _generate_methodology_note(self) -> str:
        """Generate methodology and limitations section."""
        return """---

## Methodology & Limitations

### Assessment Methodology

This AI-Native Assessment employs a signal-detection approach:

1. **Signal Extraction**: Natural language processing of company descriptions, news, and public materials
2. **Capability Classification**: Pattern matching against defined AI capability taxonomies
3. **Confidence Scoring**: Evidence-based confidence calculation from signal frequency and context
4. **Maturity Classification**: Aggregate scoring across native and adoption dimensions

### Signal Categories

| Level | Definition | Weight |
|-------|------------|--------|
| **Core** | Explicit AI-native positioning ("AI-first", "ML platform") | 3x |
| **Strong** | Clear AI terminology ("predictive analytics", "AI-powered") | 2x |
| **Moderate** | Related concepts ("data-driven", "smart") | 1x |

### Capability Taxonomy

Eight primary AI capability domains are assessed:
1. **Predictive Analytics** — Trend analysis, risk prediction, demand forecasting
2. **Natural Language Processing** — Text analysis, chatbots, document processing
3. **Computer Vision** — Image recognition, visual inspection, OCR
4. **Optimization** — Resource allocation, scheduling, load balancing
5. **Anomaly Detection** — Fraud detection, fault detection, outlier identification
6. **Forecasting** — Time series analysis, demand prediction, price forecasting
7. **Automation** — Intelligent automation, RPA, adaptive systems
8. **Recommendation** — Personalization, suggestion engines, next-best-action

### Limitations

⚠️ **Important Caveats:**

1. **Evidence Dependency**: Assessment quality depends on richness of publicly available data
2. **False Negatives**: AI capabilities may exist but not be publicly documented
3. **Signal Ambiguity**: Some terms ("smart", "intelligent") may have non-AI meanings
4. **Temporal Variance**: AI capabilities evolve rapidly; this is a point-in-time assessment
5. **Depth vs. Breadth**: This assessment evaluates capability presence, not implementation quality

### Recommended Follow-Up

For investment-grade confidence, supplement this assessment with:
- Technical due diligence interviews with engineering leadership
- Review of technical architecture documentation
- Analysis of AI/ML team composition and credentials
- Evaluation of proprietary data assets and training pipelines
- Assessment of production AI system performance metrics

---

*Generated by Solstein Intelligence Platform — Epic 6: AI-Native Assessment*
*Assessment based on publicly available data — confidence levels reflect data availability*
"""

    def _rating_from_score(self, score: float) -> str:
        """Convert score to rating label."""
        if score >= 8:
            return "STRONG"
        elif score >= 6:
            return "GOOD"
        elif score >= 4:
            return "MODERATE"
        elif score >= 2:
            return "LIMITED"
        return "MINIMAL"

    def _next_stage_requirements(self, assessment: AIAssessment) -> str:
        """Generate next stage requirements based on current level."""
        requirements = {
            AISignalLevel.ABSENT: "Move from Absent → Experimental:\n- Establish AI strategy with identified use cases\n- Begin pilot projects in high-ROI domains\n- Build foundational data infrastructure",
            AISignalLevel.EXPERIMENTAL: "Move from Experimental → Adopted:\n- Productionize successful pilots\n- Invest in ML engineering capabilities\n- Integrate AI into core business processes",
            AISignalLevel.ADOPTED: "Move from Adopted → Native:\n- Embed ML at architectural level\n- Develop proprietary algorithms and models\n- Build AI-first product positioning",
            AISignalLevel.NATIVE: "Maintain Native position:\n- Continue R&D investment in advanced techniques\n- Expand AI capabilities into new domains\n- Develop defensive IP around core algorithms",
        }
        return requirements.get(assessment.signal_level, "Continue capability development")

    def _gap_risk_assessment(self, assessment: AIAssessment) -> str:
        """Generate risk assessment based on gaps."""
        gap_count = len(assessment.gaps)
        if gap_count >= 5:
            return "**HIGH RISK**: Significant capability gaps suggest narrow AI focus or early-stage maturity. May be vulnerable to competitors with broader AI capabilities."
        elif gap_count >= 3:
            return "**MODERATE RISK**: Several undetected capabilities may indicate strategic focus or development priorities. Assess whether gaps represent competitive disadvantage."
        elif gap_count >= 1:
            return "**LOW RISK**: Minor capability gaps are normal; most companies focus on specific AI domains aligned with their value proposition."
        return "**MINIMAL RISK**: Comprehensive AI capability coverage suggests mature, well-rounded AI organization."

    def to_dict(self, assessment: AIAssessment) -> dict[str, Any]:
        """Export assessment to dictionary.

        Args:
            assessment: AI assessment

        Returns:
            Dictionary representation
        """
        return assessment.to_dict()


class AIAssessmentExporter:
    """Export AI assessments to various formats."""

    def __init__(self):
        """Initialize exporter."""
        self.report_generator = AIAssessmentReportGenerator()

    def to_markdown(self, assessment: AIAssessment) -> str:
        """Export assessment to markdown.

        Args:
            assessment: AI assessment

        Returns:
            Markdown string
        """
        return self.report_generator.generate(assessment)

    def to_dict(self, assessment: AIAssessment) -> dict[str, Any]:
        """Export assessment to dictionary.

        Args:
            assessment: AI assessment

        Returns:
            Dictionary representation
        """
        return self.report_generator.to_dict(assessment)

    def generate_comparison_table(self, assessments: list[AIAssessment]) -> str:
        """Generate comparison table for multiple companies.

        Args:
            assessments: List of AI assessments

        Returns:
            Markdown comparison table
        """
        if not assessments:
            return "No companies to compare"

        header = "| Company | Signal | Score | Native | Adoption | Capabilities |"
        separator = "|---|---|---|---|---|---|"

        rows = []
        for assessment in assessments:
            signal_emoji = {
                AISignalLevel.NATIVE: "🧠",
                AISignalLevel.ADOPTED: "🤖",
                AISignalLevel.EXPERIMENTAL: "🔬",
                AISignalLevel.ABSENT: "⚪",
            }.get(assessment.signal_level, "⚪")

            rows.append(
                f"| {assessment.company_name} | "
                f"{signal_emoji} {assessment.signal_level.value.upper()} | "
                f"{assessment.overall_score}/10 | "
                f"{assessment.ai_native_score}/10 | "
                f"{assessment.ai_adoption_score}/10 | "
                f"{len(assessment.capabilities)} |"
            )

        avg_score = sum(a.overall_score for a in assessments) / len(assessments)
        native_count = sum(1 for a in assessments if a.signal_level == AISignalLevel.NATIVE)
        adopted_count = sum(1 for a in assessments if a.signal_level == AISignalLevel.ADOPTED)

        return f"""# AI-Native Assessment Comparison

{header}
{separator}
{chr(10).join(rows)}

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Companies** | {len(assessments)} |
| **Average Score** | {avg_score:.1f}/10 |
| **AI-Native** | {native_count} ({native_count / len(assessments) * 100:.0f}%) |
| **AI-Adopted** | {adopted_count} ({adopted_count / len(assessments) * 100:.0f}%) |
| **Avg Capabilities** | {sum(len(a.capabilities) for a in assessments) / len(assessments):.1f} |

---

*Generated by Solstein Intelligence Platform*
"""
