"""Narrative synthesis engine for enriching reports with LLM-generated content.

This module provides narrative synthesis capabilities for Epic 2-4 report generators,
bringing them to the same depth as Epic 6 (AI Assessment) reports.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    from .financial_models import FinancialIntelligence
    from .genealogy_models import CorporateGenealogy
    from .protocol_models import ProtocolMap


@dataclass
class NarrativeContext:
    """Context for narrative generation."""

    company_name: str
    industry: str = "energy software"
    region: str = "Europe"
    data_quality: str = "medium"


class NarrativeSynthesisEngine:
    """Generate rich narrative content for assessment reports.

    Uses LLM providers to synthesize investment thesis-style narratives
    from structured data, matching the depth of Epic 6 AI reports.
    """

    def __init__(self):
        """Initialize narrative synthesis engine."""
        self._llm_client = None

    def _get_llm_client(self):
        """Lazy-load LLM client."""
        if self._llm_client is None:
            from ..llm.enhanced_client import EnhancedLLMClient

            self._llm_client = EnhancedLLMClient()
        return self._llm_client

    async def generate_financial_thesis(
        self,
        financial_intelligence: "FinancialIntelligence",
        context: NarrativeContext,
    ) -> dict[str, str]:
        """Generate investment thesis narrative for financial analysis.

        Args:
            financial_intelligence: Financial intelligence data
            context: Narrative context

        Returns:
            Dictionary with narrative sections
        """
        try:
            # Build data summary for LLM
            data_summary = self._summarize_financial_data(financial_intelligence)

            # Generate investment thesis
            thesis_prompt = f"""As a senior Private Equity analyst, write a compelling investment thesis for {context.company_name}.

FINANCIAL DATA:
{data_summary}

CONTEXT:
- Industry: {context.industry}
- Region: {context.region}
- Data Quality: {context.data_quality}

Write 2-3 paragraphs covering:
1. Growth narrative: What is the company's growth story?
2. Financial health: Strengths and concerns
3. Investment attractiveness: Why would a PE firm be interested?

Use professional PE language. Be specific about the numbers. If data is limited, acknowledge uncertainty but provide directional assessment.

Format as markdown with **Investment Thesis** as the header."""

            thesis = await self._generate_text(thesis_prompt)

            # Generate strategic recommendations
            recommendations_prompt = f"""As a PE advisor, what are the top 3 strategic recommendations for {context.company_name}?

FINANCIAL DATA:
{data_summary}

Provide:
1. Priority action items for value creation
2. Risk mitigation strategies
3. Growth acceleration opportunities

Be specific and actionable. Format as a bulleted list with bold headers."""

            recommendations = await self._generate_text(recommendations_prompt)

            # Generate competitive context
            competitive_prompt = f"""How does {context.company_name} likely position in the competitive landscape based on these financial metrics?

FINANCIAL DATA:
{data_summary}

CONTEXT:
- Industry: {context.industry}
- Region: {context.region}

Provide a brief competitive positioning analysis (1-2 paragraphs). Consider:
- Scale relative to typical players
- Growth trajectory vs. market
- Funding stage implications

Be realistic about data limitations."""

            competitive = await self._generate_text(competitive_prompt)

            return {
                "investment_thesis": thesis or self._fallback_financial_thesis(financial_intelligence, context),
                "strategic_recommendations": recommendations or self._fallback_recommendations(),
                "competitive_context": competitive or "*Competitive analysis requires additional market data.*",
            }

        except Exception as e:
            logger.error(f"Error generating financial narrative: {e}")
            return self._fallback_financial_narratives(financial_intelligence, context)

    async def generate_genealogy_narrative(
        self,
        genealogy: "CorporateGenealogy",
        context: NarrativeContext,
    ) -> dict[str, str]:
        """Generate narrative for corporate genealogy analysis.

        Args:
            genealogy: Corporate genealogy data
            context: Narrative context

        Returns:
            Dictionary with narrative sections
        """
        try:
            data_summary = self._summarize_genealogy_data(genealogy)

            # Ownership narrative
            ownership_prompt = f"""Analyze the ownership structure of {context.company_name}.

GENEALOGY DATA:
{data_summary}

Provide a narrative analysis (1-2 paragraphs) covering:
1. Current ownership implications (independent vs. backed)
2. Historical ownership changes and what they signal
3. Strategic implications for potential acquirers

Use PE terminology. Be factual about what the ownership structure suggests."""

            ownership = await self._generate_text(ownership_prompt)

            # M&A narrative
            ma_prompt = f"""Analyze the M&A history of {context.company_name}.

GENEALOGY DATA:
{data_summary}

Provide analysis (1-2 paragraphs) of:
1. Acquisition strategy patterns (if any)
2. Integration capabilities suggested by track record
3. Potential acquisition appetite or readiness for sale

If limited data, focus on what the absence of M&A activity might imply."""

            ma_narrative = await self._generate_text(ma_prompt)

            return {
                "ownership_narrative": ownership or self._fallback_genealogy_narrative(genealogy, context),
                "ma_narrative": ma_narrative or "*M&A analysis requires more transaction data.*",
            }

        except Exception as e:
            logger.error(f"Error generating genealogy narrative: {e}")
            return self._fallback_genealogy_narratives(genealogy, context)

    async def generate_protocol_narrative(
        self,
        protocol_map: "ProtocolMap",
        context: NarrativeContext,
    ) -> dict[str, str]:
        """Generate narrative for market protocol analysis.

        Args:
            protocol_map: Protocol mapping data
            context: Narrative context

        Returns:
            Dictionary with narrative sections
        """
        try:
            data_summary = self._summarize_protocol_data(protocol_map)

            # Market entry narrative
            entry_prompt = f"""Analyze the market entry strategy of {context.company_name}.

PROTOCOL DATA:
{data_summary}

Provide strategic analysis (1-2 paragraphs) of:
1. Geographic expansion pattern and rationale
2. Regulatory complexity management
3. Market maturity mix (developed vs. emerging)

Assess whether the strategy appears deliberate or opportunistic."""

            entry = await self._generate_text(entry_prompt)

            # Expansion opportunities
            expansion_prompt = f"""Based on current market presence, identify expansion opportunities for {context.company_name}.

PROTOCOL DATA:
{data_summary}

Provide 3-5 specific expansion opportunities with:
1. Target market and rationale
2. Protocol requirements
3. Strategic fit assessment

Format as bulleted list with bold headers."""

            expansion = await self._generate_text(expansion_prompt)

            return {
                "market_entry_narrative": entry or self._fallback_protocol_narrative(protocol_map, context),
                "expansion_analysis": expansion or self._fallback_expansion_analysis(protocol_map),
            }

        except Exception as e:
            logger.error(f"Error generating protocol narrative: {e}")
            return self._fallback_protocol_narratives(protocol_map, context)

    def _summarize_financial_data(self, fi: "FinancialIntelligence") -> str:
        """Create text summary of financial data for LLM prompt."""
        lines = []

        if fi.revenue_timeline:
            latest = fi.revenue_timeline[-1]
            lines.append(f"- Current Revenue: €{latest.revenue:.1f}M ({latest.year})")

        if fi.cagr_3yr is not None:
            lines.append(f"- 3-Year CAGR: {fi.cagr_3yr}%")
        if fi.cagr_5yr is not None:
            lines.append(f"- 5-Year CAGR: {fi.cagr_5yr}%")

        lines.append(f"- Growth Trajectory: {fi.growth_trajectory.value}")
        lines.append(f"- Growth Consistency Score: {fi.growth_consistency_score}/10")

        if fi.total_funding_raised:
            lines.append(f"- Total Funding Raised: €{fi.total_funding_raised:.1f}M")
        lines.append(f"- Funding Rounds: {len(fi.funding_rounds_enhanced)}")
        lines.append(f"- Investor Quality Score: {fi.investor_quality_score}/10")
        lines.append(f"- Funding Velocity: {fi.funding_velocity.value}")

        if fi.runway_estimate_months:
            lines.append(f"- Estimated Runway: {fi.runway_estimate_months} months")

        if fi.projected_revenue_12mo:
            lines.append(f"- 12-Month Revenue Projection: €{fi.projected_revenue_12mo:.1f}M")
            lines.append(f"- Projection Confidence: {fi.projection_confidence.value}")

        if fi.primary_growth_vectors:
            lines.append(f"- Primary Growth Vectors: {len(fi.primary_growth_vectors)}")
            for v in fi.primary_growth_vectors[:3]:
                lines.append(f"  - {v.name} (impact: {v.estimated_impact}, confidence: {v.confidence:.0%})")

        return "\n".join(lines) if lines else "- Limited financial data available"

    def _summarize_genealogy_data(self, genealogy: "CorporateGenealogy") -> str:
        """Create text summary of genealogy data for LLM prompt."""
        lines = [
            f"- Ownership Type: {genealogy.ownership_type}",
        ]

        if genealogy.current_owner:
            lines.append(f"- Current Owner: {genealogy.current_owner}")

        lines.extend(
            [
                f"- Acquisitions: {genealogy.acquisition_count}",
                f"- Divestitures: {genealogy.divestiture_count}",
                f"- Mergers: {genealogy.merger_count}",
            ]
        )

        if genealogy.total_acquisition_value:
            lines.append(f"- Total Acquisition Value: €{genealogy.total_acquisition_value:.1f}M")

        if genealogy.ownership_history:
            lines.append(f"- Ownership Changes: {len(genealogy.ownership_history)}")

        if genealogy.transactions:
            lines.append(f"- Total Transactions: {len(genealogy.transactions)}")

        return "\n".join(lines)

    def _summarize_protocol_data(self, protocol_map: "ProtocolMap") -> str:
        """Create text summary of protocol data for LLM prompt."""
        lines = [
            f"- Total Countries: {protocol_map.total_countries}",
            f"- Total Protocols: {protocol_map.total_protocols}",
            f"- Geographic Diversification: {protocol_map.geographic_diversification_score}/10",
            f"- Protocol Complexity: {protocol_map.protocol_complexity_score}/10",
        ]

        if protocol_map.primary_markets:
            lines.append(f"- Primary Markets: {', '.join(protocol_map.primary_markets)}")

        if protocol_map.emerging_markets:
            lines.append(f"- Emerging Markets: {', '.join(protocol_map.emerging_markets)}")

        if protocol_map.markets:
            mature = sum(1 for m in protocol_map.markets if m.market_maturity.value == "mature")
            developing = sum(1 for m in protocol_map.markets if m.market_maturity.value == "developing")
            emerging = sum(1 for m in protocol_map.markets if m.market_maturity.value == "emerging")
            lines.append(f"- Market Mix: {mature} mature, {developing} developing, {emerging} emerging")

        return "\n".join(lines)

    async def _generate_text(self, prompt: str, system_prompt: str | None = None) -> str | None:
        """Generate text using LLM with fallback handling."""
        try:
            client = self._get_llm_client()
            result = await client.generate(prompt, system_prompt=system_prompt)
            return result
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}")
            return None

    # Fallback methods for when LLM is unavailable

    def _fallback_financial_thesis(self, fi: "FinancialIntelligence", context: NarrativeContext) -> str:
        """Generate fallback financial thesis without LLM."""
        if fi.growth_trajectory.value == "accelerating":
            growth_desc = "demonstrating strong momentum with accelerating growth"
        elif fi.growth_trajectory.value == "steady":
            growth_desc = "showing consistent, stable growth"
        elif fi.growth_trajectory.value == "decelerating":
            growth_desc = "experiencing slowing growth that warrants attention"
        else:
            growth_desc = "with limited visible growth trajectory"

        return f"""**Investment Thesis**

{context.company_name} is {growth_desc}. The company shows a growth consistency score of {fi.growth_consistency_score}/10, indicating {"reliable" if fi.growth_consistency_score >= 7 else "moderate" if fi.growth_consistency_score >= 4 else "inconsistent"} performance patterns.

Based on available data, the company presents {"an attractive" if fi.growth_consistency_score >= 7 else "a moderate" if fi.growth_consistency_score >= 4 else "a cautious"} investment profile. {"Strong funding backing and " if fi.investor_quality_score >= 7 else ""}The financial trajectory suggests {"significant upside potential" if fi.growth_trajectory.value == "accelerating" else "steady value creation potential" if fi.growth_trajectory.value == "steady" else "need for strategic repositioning"}.

*Note: This analysis is based on publicly available data. Comprehensive due diligence would require access to detailed financial statements and management discussions.*"""

    def _fallback_recommendations(self) -> str:
        """Generate fallback recommendations."""
        return """**Strategic Recommendations**

1. **Deepen Financial Analysis**: Obtain audited financials and management accounts to validate growth trajectory and profitability drivers

2. **Validate Growth Vectors**: Interview customers and assess market sizing to confirm sustainability of identified growth drivers

3. **Assess Competitive Position**: Benchmark against comparable companies to understand relative market position and differentiation

*Recommendations will be refined as additional data becomes available.*"""

    def _fallback_financial_narratives(self, fi: "FinancialIntelligence", context: NarrativeContext) -> dict[str, str]:
        """Generate all fallback financial narratives."""
        return {
            "investment_thesis": self._fallback_financial_thesis(fi, context),
            "strategic_recommendations": self._fallback_recommendations(),
            "competitive_context": "*Competitive analysis requires additional market data. Please supplement with industry benchmarks and peer comparisons.*",
        }

    def _fallback_genealogy_narrative(self, genealogy: "CorporateGenealogy", context: NarrativeContext) -> str:
        """Generate fallback genealogy narrative."""
        if genealogy.ownership_type == "independent":
            ownership_desc = "independently owned, suggesting operational autonomy"
        elif genealogy.ownership_type == "pe_backed":
            ownership_desc = "PE-backed, indicating prior institutional validation"
        elif genealogy.ownership_type == "corporate_subsidiary":
            ownership_desc = "a corporate subsidiary, with potential strategic synergies"
        else:
            ownership_desc = f"owned via {genealogy.ownership_type} structure"

        return f"""**Ownership Analysis**

{context.company_name} is {ownership_desc}. {"The ownership by " + genealogy.current_owner + " provides strategic backing" if genealogy.current_owner else "The ownership structure appears straightforward without complex holding arrangements"}.

{f"The company has an active M&A history with {genealogy.acquisition_count} acquisitions and {genealogy.divestiture_count} divestitures, suggesting a dynamic approach to portfolio management." if genealogy.acquisition_count > 0 or genealogy.divestiture_count > 0 else "The limited M&A activity may indicate either a focused organic growth strategy or early stage in the company's development."}

*Detailed ownership implications would benefit from cap table analysis and shareholder agreement review.*"""

    def _fallback_genealogy_narratives(
        self, genealogy: "CorporateGenealogy", context: NarrativeContext
    ) -> dict[str, str]:
        """Generate all fallback genealogy narratives."""
        return {
            "ownership_narrative": self._fallback_genealogy_narrative(genealogy, context),
            "ma_narrative": "*Detailed M&A analysis requires transaction-level data and post-merger integration assessments.*",
        }

    def _fallback_protocol_narrative(self, protocol_map: "ProtocolMap", context: NarrativeContext) -> str:
        """Generate fallback protocol narrative."""
        diversification = protocol_map.geographic_diversification_score

        if diversification >= 7:
            strategy_desc = "well-diversified geographic presence reducing single-market risk"
        elif diversification >= 4:
            strategy_desc = "moderate geographic diversification with potential expansion opportunities"
        else:
            strategy_desc = "concentrated market presence suggesting focused or early-stage expansion"

        return f"""**Market Entry Strategy**

{context.company_name} demonstrates a {strategy_desc}. With presence in {protocol_map.total_countries} countries and {protocol_map.total_protocols} protocol implementations, the company shows {"sophisticated" if protocol_map.protocol_complexity_score >= 7 else "developing" if protocol_map.protocol_complexity_score >= 4 else "basic"} regulatory navigation capabilities.

The market maturity mix indicates {"balanced exposure" if protocol_map.geographic_diversification_score >= 7 else "concentrated exposure"} across developed and emerging markets. {"Primary markets include " + ", ".join(protocol_map.primary_markets[:3]) if protocol_map.primary_markets else "Core market presence to be determined from operational data"}.

*Strategic assessment would benefit from market-by-market revenue contribution analysis and competitive positioning review.*"""

    def _fallback_expansion_analysis(self, protocol_map: "ProtocolMap") -> str:
        """Generate fallback expansion analysis."""
        if not protocol_map.expansion_opportunities:
            return "*Expansion opportunities to be identified based on market analysis and competitive landscape assessment.*"

        lines = ["**Expansion Opportunities**", ""]
        for opp in protocol_map.expansion_opportunities[:5]:
            lines.append(f"- **{opp}**: Requires protocol compliance and market entry investment")

        return "\n".join(lines)

    def _fallback_protocol_narratives(self, protocol_map: "ProtocolMap", context: NarrativeContext) -> dict[str, str]:
        """Generate all fallback protocol narratives."""
        return {
            "market_entry_narrative": self._fallback_protocol_narrative(protocol_map, context),
            "expansion_analysis": self._fallback_expansion_analysis(protocol_map),
        }
