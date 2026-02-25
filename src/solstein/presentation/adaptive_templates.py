"""
Task 13: Context-Aware Report Templates

Adaptive report templates that respond to data availability and company classification.
Templates adjust narrative tone and detail level based on:
- Data completeness (sparse vs rich)
- Company classification (Phoenix/Salt/Lead)
- Available metrics and signals
"""

from solstein.analytics.completeness import CompletenessCalculator
from solstein.domain.models import Company


class AdaptiveTemplates:
    """Generate context-aware report sections based on data availability and classification."""

    # Completeness thresholds
    SPARSE_THRESHOLD = 40  # < 40% complete = sparse
    MODERATE_THRESHOLD = 70  # 40-70% = moderate
    RICH_THRESHOLD = 70  # > 70% = rich

    _completeness_calculator = CompletenessCalculator()

    @staticmethod
    def get_strengths_section(company: Company) -> str:
        """Generate strengths section for ANY company (never empty).

        Adapts narrative based on:
        - Classification (Phoenix/Salt/Lead)
        - Data completeness
        - Available metrics
        """
        classification = company.classification or "Unknown"
        completeness = AdaptiveTemplates._completeness_calculator.calculate_completeness_score(company)

        if completeness < AdaptiveTemplates.SPARSE_THRESHOLD:
            return AdaptiveTemplates._sparse_strengths(company, classification)
        elif completeness < AdaptiveTemplates.RICH_THRESHOLD:
            return AdaptiveTemplates._moderate_strengths(company, classification)
        else:
            return AdaptiveTemplates._rich_strengths(company, classification)

    @staticmethod
    def _sparse_strengths(company: Company, classification: str) -> str:
        """Strengths section for data-sparse companies."""
        base = "## Identified Strengths\n\n"
        base += "**Note**: Limited data available for comprehensive analysis. "
        base += "The following strengths are identified from available sources:\n\n"

        strengths = []

        # Always find something positive
        if company.composite_score and company.composite_score >= 5.0:
            strengths.append(
                f"- **Competitive Positioning**: Composite score of {company.composite_score:.1f} indicates "
                f"{'strong' if company.composite_score >= 7 else 'solid'} market positioning"
            )

        if company.ai_maturity:
            strengths.append(f"- **AI Maturity**: {company.ai_maturity} AI capabilities identified")

        if company.financials and company.financials.revenue:
            strengths.append(
                f"- **Revenue Base**: €{company.financials.revenue:.1f}M revenue demonstrates market traction"
            )

        if company.financials and company.financials.employees:
            strengths.append(
                f"- **Team Scale**: {company.financials.employees} employees indicates organizational maturity"
            )

        if not strengths:
            strengths.append("- **Market Presence**: Company operates in competitive market segment")

        return (
            base
            + "\n".join(strengths)
            + "\n\n**Data Quality**: Limited. Additional data collection recommended for deeper analysis."
        )

    @staticmethod
    def _moderate_strengths(company: Company, classification: str) -> str:
        """Strengths section for data-moderate companies."""
        base = "## Identified Strengths\n\n"

        if classification == "Phoenix":
            base += "This high-growth company demonstrates several key strengths:\n\n"
        elif classification == "Lead":
            base += "Despite legacy positioning, this company shows notable strengths:\n\n"
        else:  # Salt
            base += "This stable company demonstrates consistent strengths:\n\n"

        strengths = []

        # Growth indicators
        if company.revenue_timeline and len(company.revenue_timeline) > 1:
            latest = company.revenue_timeline[0]
            if latest.get("yoy_growth_pct", 0) > 20:
                strengths.append(
                    f"- **Strong Revenue Growth**: {latest.get('yoy_growth_pct', 0):.0f}% YoY growth demonstrates market demand"
                )
            elif latest.get("yoy_growth_pct", 0) > 0:
                strengths.append(
                    f"- **Consistent Growth**: {latest.get('yoy_growth_pct', 0):.0f}% YoY growth shows stable trajectory"
                )

        if company.financials:
            if company.financials.revenue and company.financials.revenue > 100:
                strengths.append(
                    f"- **Scale**: €{company.financials.revenue:.1f}M revenue demonstrates market validation"
                )
            if company.ebitda_margin and company.ebitda_margin > 10:
                strengths.append(
                    f"- **Profitability**: {company.ebitda_margin:.0f}% EBITDA margin shows operational efficiency"
                )
            if company.recurring_revenue_pct and company.recurring_revenue_pct > 50:
                strengths.append(
                    f"- **Recurring Revenue**: {company.recurring_revenue_pct:.0f}% recurring revenue provides predictability"
                )
        # Technology
        if company.ai_maturity and company.ai_maturity in ["Strong", "Very Strong"]:
            strengths.append(
                f"- **AI Capabilities**: {company.ai_maturity} AI maturity positions company for future growth"
            )

        if company.saas_maturity and company.saas_maturity >= 7:
            strengths.append("- **SaaS Model**: Mature SaaS implementation enables scalability")

        # Team
        if company.financials and company.financials.employees and company.financials.employees > 100:
            strengths.append(f"- **Team**: {company.financials.employees} employees indicates organizational depth")

        if not strengths:
            strengths.append("- **Market Position**: Established presence in competitive segment")

        return base + "\n".join(strengths)

    @staticmethod
    def _rich_strengths(company: Company, classification: str) -> str:
        """Strengths section for data-rich companies with detailed analysis."""
        base = "## Identified Strengths\n\n"

        if classification == "Phoenix":
            base += "This high-growth company demonstrates exceptional strengths across multiple dimensions:\n\n"
        elif classification == "Lead":
            base += "Despite legacy positioning, this company shows significant strengths that warrant attention:\n\n"
        else:  # Salt
            base += "This stable, mature company demonstrates consistent strengths:\n\n"

        strengths = []

        # Growth trajectory
        if company.revenue_timeline and len(company.revenue_timeline) > 1:
            latest = company.revenue_timeline[0]
            growth = latest.get("yoy_growth_pct", 0)
            if growth > 50:
                strengths.append(
                    f"- **Exceptional Growth**: {growth:.0f}% YoY revenue growth demonstrates strong market demand and execution"
                )
            elif growth > 20:
                strengths.append(
                    f"- **Strong Growth**: {growth:.0f}% YoY growth trajectory shows market traction and scaling capability"
                )
            elif growth > 0:
                strengths.append(
                    f"- **Consistent Growth**: {growth:.0f}% YoY growth demonstrates stable business model"
                )

        # Financial health - detailed
        if company.financials:
            if company.financials.revenue:
                strengths.append(
                    f"- **Revenue Scale**: €{company.financials.revenue:.1f}M revenue with "
                    f"{company.revenue_per_employee_eur_k:.0f}K per employee shows operational efficiency"
                )

            if company.ebitda_margin:
                if company.ebitda_margin > 30:
                    strengths.append(
                        f"- **Exceptional Profitability**: {company.ebitda_margin:.0f}% EBITDA margin demonstrates pricing power"
                    )
                elif company.ebitda_margin > 15:
                    strengths.append(
                        f"- **Strong Profitability**: {company.ebitda_margin:.0f}% EBITDA margin shows operational excellence"
                    )
                elif company.ebitda_margin > 0:
                    strengths.append(
                        f"- **Path to Profitability**: {company.ebitda_margin:.0f}% EBITDA margin demonstrates improving unit economics"
                    )

            if company.recurring_revenue_pct:
                if company.recurring_revenue_pct > 80:
                    strengths.append(
                        f"- **Predictable Revenue**: {company.recurring_revenue_pct:.0f}% recurring revenue provides strong cash flow visibility"
                    )
                elif company.recurring_revenue_pct > 50:
                    strengths.append(
                        f"- **Recurring Revenue Model**: {company.recurring_revenue_pct:.0f}% recurring revenue enables predictable growth"
                    )
        # Technology and AI
        if company.ai_score and company.ai_score >= 7:
            strengths.append(
                f"- **AI Leadership**: AI score of {company.ai_score}/10 positions company at forefront of AI adoption"
            )
        elif company.ai_maturity and company.ai_maturity in ["Strong", "Very Strong"]:
            strengths.append(
                f"- **Advanced AI Capabilities**: {company.ai_maturity} AI maturity demonstrates competitive advantage"
            )

        if company.saas_maturity and company.saas_maturity >= 8:
            strengths.append("- **SaaS Excellence**: Mature SaaS implementation with strong product-market fit")
        elif company.saas_maturity and company.saas_maturity >= 6:
            strengths.append("- **SaaS Model**: Well-developed SaaS capabilities enable scalability")

        # Funding and investors
        if company.total_funding_raised_eur and company.total_funding_raised_eur > 50:
            strengths.append(
                f"- **Investor Confidence**: €{company.total_funding_raised_eur:.0f}M raised demonstrates investor validation"
            )

        if company.lead_investors and len(company.lead_investors) > 0:
            top_investors = ", ".join(company.lead_investors[:2])
            strengths.append(f"- **Quality Investors**: Backed by {top_investors} and others")

        # Team
        if company.financials and company.financials.employees:
            if company.financials.employees > 500:
                strengths.append(
                    f"- **Established Organization**: {company.financials.employees} employees demonstrates organizational maturity and execution capability"
                )
            elif company.financials.employees > 100:
                strengths.append(
                    f"- **Strong Team**: {company.financials.employees} employees with specialized expertise"
                )
            else:
                strengths.append(
                    f"- **Focused Team**: {company.financials.employees} employees demonstrates lean, efficient operations"
                )

        # Customers
        if company.key_customers and len(company.key_customers) > 0:
            strengths.append(
                f"- **Customer Traction**: {len(company.key_customers)}+ key customers including {company.key_customers[0]}"
            )

        if not strengths:
            strengths.append("- **Market Position**: Established competitive presence with multiple growth vectors")

        return base + "\n".join(strengths)

    @staticmethod
    def get_data_quality_note(company: Company) -> str:
        """Generate data quality note based on completeness."""
        completeness = AdaptiveTemplates._completeness_calculator.calculate_completeness_score(company)

        if completeness < AdaptiveTemplates.SPARSE_THRESHOLD:
            return f"**Data Quality**: Limited ({completeness:.0f}% complete). Additional data collection recommended."
        elif completeness < AdaptiveTemplates.RICH_THRESHOLD:
            return f"**Data Quality**: Moderate ({completeness:.0f}% complete). Analysis based on available sources."
        else:
            return f"**Data Quality**: Comprehensive ({completeness:.0f}% complete). Analysis based on extensive data."

    @staticmethod
    def get_classification_narrative(company: Company) -> str:
        """Get narrative introduction based on classification."""
        classification = company.classification or "Unknown"
        score = company.composite_score or 0

        if classification == "Phoenix":
            return (
                f"**{company.name}** is a high-growth company with a composite score of {score:.1f}. "
                f"The company demonstrates strong market traction, rapid growth, and significant competitive advantages. "
                f"This represents a high-potential investment opportunity."
            )
        elif classification == "Lead":
            return (
                f"**{company.name}** is a legacy-positioned company with a composite score of {score:.1f}. "
                f"While facing headwinds from legacy systems, the company has opportunities for transformation and value creation. "
                f"Success depends on execution of modernization initiatives."
            )
        else:  # Salt
            return (
                f"**{company.name}** is a stable, mature company with a composite score of {score:.1f}. "
                f"The company demonstrates consistent performance and market presence. "
                f"This represents a solid, lower-risk investment with steady returns."
            )
