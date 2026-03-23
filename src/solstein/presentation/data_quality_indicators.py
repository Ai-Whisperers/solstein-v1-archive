"""
Task 14: Data Quality Indicators in Reports

Provides visual indicators and metadata for data quality in reports.
Includes confidence levels, data provenance, and completeness metrics.
"""

from typing import Any

from solstein.analytics.completeness import CompletenessCalculator, DataQualityTier
from solstein.domain.models import Company, ConfidenceLevel


class DataQualityIndicators:
    """Generate data quality indicators and provenance information for reports."""

    # Visual indicators for confidence levels
    CONFIDENCE_INDICATORS = {
        ConfidenceLevel.CONFIRMED: "✓",  # Confirmed data
        ConfidenceLevel.ESTIMATED: "~",  # Estimated data
        ConfidenceLevel.UNKNOWN: "?",  # Unknown data
    }

    # Tier descriptions
    TIER_DESCRIPTIONS = {
        DataQualityTier.COMPLETE: "Comprehensive data with high confidence",
        DataQualityTier.PARTIAL: "Moderate data with mixed confidence levels",
        DataQualityTier.MINIMAL: "Limited data requiring careful interpretation",
        DataQualityTier.INSUFFICIENT: "Sparse data - use with caution",
    }

    _completeness_calculator = CompletenessCalculator()

    @staticmethod
    def get_completeness_score(company: Company) -> float:
        """Get completeness score for a company (0-100)."""
        return DataQualityIndicators._completeness_calculator.calculate_completeness_score(company)

    @staticmethod
    def get_data_quality_tier(company: Company) -> DataQualityTier:
        """Get data quality tier for a company."""
        score = DataQualityIndicators.get_completeness_score(company)
        return DataQualityIndicators._completeness_calculator.assign_tier(score)

    @staticmethod
    def get_executive_summary_section(company: Company) -> str:
        """Generate data quality section for executive summary."""
        score = DataQualityIndicators.get_completeness_score(company)
        tier = DataQualityIndicators.get_data_quality_tier(company)
        description = DataQualityIndicators.TIER_DESCRIPTIONS.get(tier, "Unknown")

        return f"""## Data Quality Assessment

**Completeness Score**: {score:.0f}% | **Tier**: {tier.value}

{description}

**What This Means**:
- Scores 80-100%: Comprehensive data with high confidence in analysis
- Scores 50-79%: Moderate data; analysis is directionally sound but may have gaps
- Scores 20-49%: Limited data; use for directional insights only
- Scores 0-19%: Sparse data; treat as preliminary assessment

**Confidence Indicators Used in This Report**:
- ✓ = Confirmed from primary sources (high confidence)
- ~ = Estimated from available data (medium confidence)
- ? = Unknown or unavailable (low confidence)
"""

    @staticmethod
    def get_metric_with_indicator(value: Any, confidence: ConfidenceLevel | None = None) -> str:
        """Format a metric value with confidence indicator."""
        if value is None:
            return "? N/A"

        indicator = DataQualityIndicators.CONFIDENCE_INDICATORS.get(confidence or ConfidenceLevel.UNKNOWN, "?")

        if isinstance(value, float):
            return f"{indicator} {value:.1f}"
        elif isinstance(value, int):
            return f"{indicator} {value:,}"
        else:
            return f"{indicator} {value}"

    @staticmethod
    def get_data_provenance_table(company: Company) -> str:
        """Generate data provenance table showing source and confidence for key metrics."""
        rows = []

        # Financial metrics
        fin = company.financials
        metrics = [
            ("Revenue", fin.revenue if fin else None, fin.revenue_confidence if fin else None),
            ("Employees", fin.employees if fin else None, fin.employees_confidence if fin else None),
            ("Growth Rate", fin.growth_rate if fin else None, fin.growth_confidence if fin else None),
            ("Profit Margin", company.profit_margin, None),
            ("EBITDA Margin", company.ebitda_margin, None),
            ("Recurring Revenue %", company.recurring_revenue_pct, None),
            ("Funding Raised", fin.funding_raised if fin else None, fin.funding_confidence if fin else None),
            ("Valuation", fin.valuation if fin else None, fin.valuation_confidence if fin else None),
        ]

        # AI/Tech metrics
        tech_metrics = [
            ("AI Maturity", company.ai_maturity, None),
            ("AI Score", company.ai_score, None),
            ("SaaS Maturity", company.saas_maturity, None),
        ]

        # Build table
        rows.append("| Metric | Value | Confidence | Source |")
        rows.append("|--------|-------|------------|--------|")

        for metric_name, value, confidence in metrics + tech_metrics:
            if value is not None:
                indicator = DataQualityIndicators.CONFIDENCE_INDICATORS.get(confidence or ConfidenceLevel.UNKNOWN, "?")
                source = company.metric_sources.get(metric_name.lower().replace(" ", "_"), ["Unknown"])[0]
                rows.append(f"| {metric_name} | {value} | {indicator} | {source} |")

        return "\n".join(rows)

    @staticmethod
    def get_data_quality_flags(company: Company) -> list[str]:
        """Get list of data quality flags/warnings for a company."""
        flags = []
        score = DataQualityIndicators.get_completeness_score(company)

        # Sparse data warning
        if score < 40:
            flags.append("⚠️ **Sparse Data**: This company has limited data. Treat analysis as preliminary.")

        # Missing critical fields
        if not company.financials or company.financials.revenue is None:
            flags.append("⚠️ **No Revenue Data**: Revenue information is unavailable.")

        if not company.financials or company.financials.employees is None:
            flags.append("⚠️ **No Employee Count**: Employee data is unavailable.")

        # Contradictions
        if company.ai_maturity and company.ai_score is not None:
            if company.ai_maturity == "None" and company.ai_score > 5:
                flags.append("⚠️ **Contradiction**: AI maturity is 'None' but AI score is high.")
            elif company.ai_maturity in ["Strong", "Very Strong"] and company.ai_score < 5:
                flags.append("⚠️ **Contradiction**: AI maturity is strong but AI score is low.")

        # Estimated data warning
        estimated_count = sum(
            1
            for conf in (
                [
                    company.financials.revenue_confidence,
                    company.financials.employees_confidence,
                    company.financials.growth_confidence,
                ]
                if company.financials
                else []
            )
            if conf == ConfidenceLevel.ESTIMATED
        )
        if estimated_count >= 2:
            flags.append(f"⚠️ **Multiple Estimates**: {estimated_count} key metrics are estimated.")

        return flags

    @staticmethod
    def get_data_confidence_section(company: Company) -> str:
        """Generate comprehensive data confidence section for reports."""
        flags = DataQualityIndicators.get_data_quality_flags(company)
        provenance = DataQualityIndicators.get_data_provenance_table(company)

        section = "## Data Confidence & Provenance\n\n"

        if flags:
            section += "### Quality Flags\n\n"
            for flag in flags:
                section += f"{flag}\n"
            section += "\n"

        section += "### Data Sources & Confidence\n\n"
        section += provenance
        section += "\n\n"

        section += "### Interpretation Guide\n\n"
        section += (
            "- **✓ Confirmed**: Data from official sources (financial reports, company website, verified databases)\n"
        )
        section += "- **~ Estimated**: Data derived from available information or industry benchmarks\n"
        section += "- **? Unknown**: Data not available from accessible sources\n"

        return section

    @staticmethod
    def get_metric_confidence_summary(company: Company) -> dict[str, str]:
        """Get confidence summary for all key metrics."""
        summary = {}

        # Financial metrics
        fin = company.financials
        summary["Revenue"] = DataQualityIndicators.CONFIDENCE_INDICATORS.get(fin.revenue_confidence if fin else None, "?")
        summary["Employees"] = DataQualityIndicators.CONFIDENCE_INDICATORS.get(
            fin.employees_confidence if fin else None, "?"
        )
        summary["Growth Rate"] = DataQualityIndicators.CONFIDENCE_INDICATORS.get(
            fin.growth_confidence if fin else None, "?"
        )
        summary["Funding"] = DataQualityIndicators.CONFIDENCE_INDICATORS.get(fin.funding_confidence if fin else None, "?")
        summary["Valuation"] = DataQualityIndicators.CONFIDENCE_INDICATORS.get(
            fin.valuation_confidence if fin else None, "?"
        )

        # Derived metrics (always estimated if present)
        if company.profit_margin is not None:
            summary["Profit Margin"] = "~"
        if company.ebitda_margin is not None:
            summary["EBITDA Margin"] = "~"
        if company.recurring_revenue_pct is not None:
            summary["Recurring Revenue %"] = "~"

        # AI/Tech metrics
        if company.ai_maturity is not None:
            summary["AI Maturity"] = "✓"  # From structured data
        if company.ai_score is not None:
            summary["AI Score"] = "~"  # Calculated/estimated
        if company.saas_maturity is not None:
            summary["SaaS Maturity"] = "~"  # Calculated/estimated

        return summary
