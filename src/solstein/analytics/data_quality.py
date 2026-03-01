"""Data quality calculator for company profiles (EPIC-FIX-005).

Provides data quality scoring and reporting for company profiles.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class DataQualityReport:
    """Data quality report for a company."""

    company_name: str
    overall_score: float  # 0.0 - 1.0
    fields_present: int
    fields_total: int
    category_scores: Dict[str, float]
    missing_fields: List[str]
    recommendations: List[str]


class DataQualityCalculator:
    """Calculate data quality scores for company profiles."""

    # Define required fields by category
    FIELD_CATEGORIES = {
        "identity": ["company_name", "description", "industry", "founded_year", "headquarters", "website", "country"],
        "financials": ["revenue", "growth_rate", "profit_margin", "funding_raised", "valuation", "employees"],
        "technology": ["ai_maturity", "ai_score", "saas_maturity", "tech_stack"],
        "market": ["geographic_presence", "classification", "competitors"],
        "enrichment": ["data_quality_score", "enrichment_source_count", "confidence_levels", "source_links"],
    }

    def __init__(self):
        self.all_fields = []
        for fields in self.FIELD_CATEGORIES.values():
            self.all_fields.extend(fields)

    def calculate_quality(self, company: Dict[str, Any]) -> DataQualityReport:
        """Calculate data quality for a company."""
        fields_present = 0
        fields_total = len(self.all_fields)
        missing_fields = []
        category_scores = {}
        recommendations = []

        for category, fields in self.FIELD_CATEGORIES.items():
            category_present = 0
            category_total = len(fields)

            for field in fields:
                if self._has_value(company, field):
                    fields_present += 1
                    category_present += 1
                else:
                    missing_fields.append(f"{category}.{field}")

            category_scores[category] = category_present / category_total if category_total > 0 else 0.0

        overall_score = fields_present / fields_total if fields_total > 0 else 0.0

        # Generate recommendations
        if category_scores.get("financials", 0) < 0.5:
            recommendations.append("Add more financial data (revenue, funding, valuation)")
        if category_scores.get("technology", 0) < 0.5:
            recommendations.append("Enrich technology signals (AI maturity, tech stack)")
        if category_scores.get("enrichment", 0) < 0.5:
            recommendations.append("Run enrichment pipeline to add source confidence")

        return DataQualityReport(
            company_name=company.get("company_name", "Unknown"),
            overall_score=round(overall_score, 2),
            fields_present=fields_present,
            fields_total=fields_total,
            category_scores={k: round(v, 2) for k, v in category_scores.items()},
            missing_fields=missing_fields[:10],  # Top 10 missing
            recommendations=recommendations,
        )

    def _has_value(self, company: Dict[str, Any], field: str) -> bool:
        """Check if a field has a meaningful value."""
        value = company.get(field)
        if value is None:
            return False
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        if isinstance(value, str) and value.strip() == "":
            return False
        if isinstance(value, (int, float)) and value == 0:
            # Zero might be valid for some fields
            return field in ["growth_rate", "profit_margin"]
        return True

    def generate_market_report(self, companies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate aggregate data quality report for a market."""
        reports = [self.calculate_quality(c) for c in companies]

        if not reports:
            return {"error": "No companies to analyze"}

        avg_score = sum(r.overall_score for r in reports) / len(reports)

        # Category averages
        category_avgs = {}
        for category in self.FIELD_CATEGORIES.keys():
            scores = [r.category_scores.get(category, 0) for r in reports]
            category_avgs[category] = round(sum(scores) / len(scores), 2) if scores else 0.0

        # Quality distribution
        quality_distribution = {
            "excellent": sum(1 for r in reports if r.overall_score >= 0.8),
            "good": sum(1 for r in reports if 0.6 <= r.overall_score < 0.8),
            "fair": sum(1 for r in reports if 0.4 <= r.overall_score < 0.6),
            "poor": sum(1 for r in reports if r.overall_score < 0.4),
        }

        return {
            "market_average_score": round(avg_score, 2),
            "companies_analyzed": len(reports),
            "category_averages": category_avgs,
            "quality_distribution": quality_distribution,
            "company_reports": [
                {
                    "name": r.company_name,
                    "score": r.overall_score,
                    "fields_present": r.fields_present,
                    "fields_total": r.fields_total,
                }
                for r in reports
            ],
        }


# Convenience function
def calculate_company_quality(company: Dict[str, Any]) -> DataQualityReport:
    """Calculate data quality for a single company."""
    calculator = DataQualityCalculator()
    return calculator.calculate_quality(company)


def calculate_market_quality(companies: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate data quality for a market of companies."""
    calculator = DataQualityCalculator()
    return calculator.generate_market_report(companies)
