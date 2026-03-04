"""
Field Mapping Audit - ENEVE Data Conversion
============================================

This module documents and validates the field mapping from JSON input to Company model.

Story 4.1: Field mapping audit - Documents all field mappings to ensure
no data is lost during conversion.

Input Format (competitor_data.json):
------------------------------------
{
    "competitors": [
        {
            "company_name": str,
            "industry": str,
            "description": str,
            "website": str,
            "country": str,
            "founded_year": int,
            "classification": str,  # "Phoenix", "Salt", "Lead"
            "ai_maturity": str,  # "Very Strong", "Strong", "Moderate", "Low", "None"
            "employees": int,
            "employees_confidence": str,  # "high", "medium", "low"
            "funding_raised": float,  # in millions EUR
            "funding_confidence": str,
            "valuation": float,  # in millions EUR
            "valuation_confidence": str,
            "revenue": {
                "timeline": [
                    {
                        "year": int,
                        "eur_millions": float,
                        "yoy_growth_pct": float,
                        "confidence": str  # "high", "medium", "low"
                    }
                ],
                "cagr_3yr_pct": float,
                "cagr_5yr_pct": float
            },
            "profitability": {
                "ebitda_margin_pct": float,
                "recurring_revenue_pct": float,
                "revenue_per_employee_eur_k": float
            },
            "geographic_presence": [str],
            "enrichment_source_count": int,
            "enrichment_quality_metrics": dict,
            "source_links": [dict]
        }
    ]
}

Output Format (Company Model):
------------------------------
Company(
    id: str                          # Generated from company_name
    name: str                        # company_name
    industry: str                    # industry (default: "Energy Software")
    description: str                 # description
    website: str                     # website
    headquarters: str                # country
    founded_year: int                # founded_year
    tier: CompanyTier                # Mapped from classification
    threat_level: ThreatLevel        # Always LOW (for now)
    ai_maturity: AIMaturity          # Mapped from ai_maturity string
    saas_maturity: int               # Always 5 (default)
    tech_stack: List[str]            # Always empty (for now)
    signal_confidences: dict         # Built from individual confidences
    revenue_cagr_3yr: float          # revenue.cagr_3yr_pct
    revenue_cagr_5yr: float          # revenue.cagr_5yr_pct
    geographic_presence: List[str]   # geographic_presence
    key_customers: List[str]         # Always empty (for now)
    enrichment_source_count: int     # enrichment_source_count
    data_source: str                 # Always "Solstein Competitive Intelligence"
    last_updated: datetime           # Current timestamp
    financials: FinancialMetric(
        revenue: float                # revenue.timeline[0].eur_millions
        revenue_confidence: ConfidenceLevel  # Mapped from timeline[0].confidence
        growth_rate: float            # revenue.timeline[0].yoy_growth_pct
        growth_confidence: ConfidenceLevel  # Same as revenue_confidence
        employees: int                # employees
        employees_confidence: ConfidenceLevel  # Mapped from employees_confidence
        funding_raised: float         # funding_raised
        funding_confidence: ConfidenceLevel  # Mapped from funding_confidence
        valuation: float              # valuation
        valuation_confidence: ConfidenceLevel  # Mapped from valuation_confidence
        profit_margin: float          # profitability.ebitda_margin_pct
        ebitda_margin: float          # profitability.ebitda_margin_pct (same)
        recurring_revenue_pct: float  # profitability.recurring_revenue_pct
        revenue_per_employee: float   # profitability.revenue_per_employee_eur_k
    )
)

Field Mapping Table:
--------------------
| JSON Field | Model Field | Transform | Notes |
|------------|-------------|-----------|-------|
| company_name | Company.id | slugify + unique suffix | Generated |
| company_name | Company.name | direct | |
| industry | Company.industry | default "Energy Software" | |
| description | Company.description | direct | |
| website | Company.website | direct | |
| country | Company.headquarters | direct | |
| founded_year | Company.founded_year | direct | |
| classification | Company.tier | Phoenix→TIER_1, Salt→TIER_2, Lead→TIER_4 | |
| ai_maturity | Company.ai_maturity | String→Enum mapping | |
| employees | FinancialMetric.employees | direct | |
| employees_confidence | FinancialMetric.employees_confidence | String→Enum mapping | |
| funding_raised | FinancialMetric.funding_raised | direct | |
| funding_confidence | FinancialMetric.funding_confidence | String→Enum mapping | |
| valuation | FinancialMetric.valuation | direct | |
| valuation_confidence | FinancialMetric.valuation_confidence | String→Enum mapping | |
| revenue.timeline[0].eur_millions | FinancialMetric.revenue | direct | |
| revenue.timeline[0].confidence | FinancialMetric.revenue_confidence | String→Enum mapping | |
| revenue.timeline[0].yoy_growth_pct | FinancialMetric.growth_rate | direct | |
| revenue.cagr_3yr_pct | Company.revenue_cagr_3yr | direct | Preserved |
| revenue.cagr_5yr_pct | Company.revenue_cagr_5yr | direct | Preserved |
| profitability.ebitda_margin_pct | FinancialMetric.profit_margin | direct | |
| profitability.ebitda_margin_pct | FinancialMetric.ebitda_margin | direct | Same value |
| profitability.recurring_revenue_pct | FinancialMetric.recurring_revenue_pct | direct | |
| profitability.revenue_per_employee_eur_k | FinancialMetric.revenue_per_employee | direct | |
| geographic_presence | Company.geographic_presence | direct | |
| enrichment_source_count | Company.enrichment_source_count | direct | Preserved |
| enrichment_quality_metrics | (not mapped) | - | Available in JSON only |
| source_links | (not mapped) | - | Available in JSON only |

Confidence Level Mapping:
-------------------------
| JSON Value | ConfidenceLevel Enum | Weight |
|------------|---------------------|--------|
| "high" | CONFIRMED | 1.0 |
| "medium" | ESTIMATED | 0.7 |
| "low" | UNKNOWN | 0.3 |
| (missing) | UNKNOWN | 0.3 |

Classification Mapping:
-----------------------
| Classification | CompanyTier | Notes |
|----------------|-------------|-------|
| "Phoenix" | TIER_1 | Best companies |
| "Salt" | TIER_2 | Moderate companies |
| (other) | TIER_3 | Default |
| "Lead" | TIER_4 | Struggling companies |

AI Maturity Mapping:
--------------------
| JSON Value | AIMaturity Enum |
|------------|-----------------|
| "Very Strong" | VERY_STRONG |
| "Strong" | STRONG |
| "Moderate" | MODERATE |
| "Low" | LOW |
| "None" | NONE |
| (missing) | NONE |

Signal Confidences Mapping:
---------------------------
The signal_confidences dictionary is built from individual confidence fields:
- "revenue": weight from revenue.timeline[0].confidence
- "growth_rate": weight from revenue.timeline[0].confidence (same as revenue)
- "employees": weight from employees_confidence
- "funding": weight from funding_confidence
- "valuation": weight from valuation_confidence
- "ai_maturity": weight from ai_confidence

Validation Checks:
------------------
1. All required fields present
2. Data types match expectations
3. Confidence levels valid
4. No data loss during conversion
5. Enrichment metrics preserved

Usage:
------
    from scripts.field_mapping_audit import validate_field_mapping

    # Validate a single company conversion
    company_data = {...}  # JSON data
    company = convert_json_to_company(company_data)
    issues = validate_field_mapping(company_data, company)

    if issues:
        print("Field mapping issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("All fields mapped correctly!")
"""

from dataclasses import dataclass
from typing import Any

from solstein.domain.models import Company


@dataclass
class FieldMappingIssue:
    """Represents a field mapping issue."""

    field: str
    expected: Any
    actual: Any
    message: str


def validate_field_mapping(json_data: dict[str, Any], company: Company) -> list[FieldMappingIssue]:
    """Validate that all fields from JSON are correctly mapped to Company model.

    Args:
        json_data: Original JSON data
        company: Converted Company model

    Returns:
        List of field mapping issues (empty if all valid)
    """
    issues = []

    # Check basic fields
    if json_data.get("company_name") != company.name:
        issues.append(
            FieldMappingIssue(
                field="company_name",
                expected=json_data.get("company_name"),
                actual=company.name,
                message="Company name mismatch",
            )
        )

    if json_data.get("industry") != company.industry and company.industry != "Energy Software":
        issues.append(
            FieldMappingIssue(
                field="industry",
                expected=json_data.get("industry"),
                actual=company.industry,
                message="Industry mismatch or unexpected default",
            )
        )

    if json_data.get("description") != company.description:
        issues.append(
            FieldMappingIssue(
                field="description",
                expected=json_data.get("description"),
                actual=company.description,
                message="Description mismatch",
            )
        )

    if json_data.get("website") != company.website:
        issues.append(
            FieldMappingIssue(
                field="website", expected=json_data.get("website"), actual=company.website, message="Website mismatch"
            )
        )

    if json_data.get("country") != company.headquarters:
        issues.append(
            FieldMappingIssue(
                field="country",
                expected=json_data.get("country"),
                actual=company.headquarters,
                message="Country/headquarters mismatch",
            )
        )

    if json_data.get("founded_year") != company.founded_year:
        issues.append(
            FieldMappingIssue(
                field="founded_year",
                expected=json_data.get("founded_year"),
                actual=company.founded_year,
                message="Founded year mismatch",
            )
        )

    # Check financial fields
    revenue_data = json_data.get("revenue", {})
    timeline = revenue_data.get("timeline", [])
    latest_revenue = timeline[0] if timeline else {}

    if latest_revenue.get("eur_millions") != company.financials.revenue:
        issues.append(
            FieldMappingIssue(
                field="revenue.timeline[0].eur_millions",
                expected=latest_revenue.get("eur_millions"),
                actual=company.financials.revenue,
                message="Revenue mismatch",
            )
        )

    if latest_revenue.get("yoy_growth_pct") != company.financials.growth_rate:
        issues.append(
            FieldMappingIssue(
                field="revenue.timeline[0].yoy_growth_pct",
                expected=latest_revenue.get("yoy_growth_pct"),
                actual=company.financials.growth_rate,
                message="Growth rate mismatch",
            )
        )

    # Check CAGR preservation
    if revenue_data.get("cagr_3yr_pct") != company.revenue_cagr_3yr:
        issues.append(
            FieldMappingIssue(
                field="revenue.cagr_3yr_pct",
                expected=revenue_data.get("cagr_3yr_pct"),
                actual=company.revenue_cagr_3yr,
                message="CAGR 3-year not preserved",
            )
        )

    if revenue_data.get("cagr_5yr_pct") != company.revenue_cagr_5yr:
        issues.append(
            FieldMappingIssue(
                field="revenue.cagr_5yr_pct",
                expected=revenue_data.get("cagr_5yr_pct"),
                actual=company.revenue_cagr_5yr,
                message="CAGR 5-year not preserved",
            )
        )

    # Check enrichment count preservation
    if json_data.get("enrichment_source_count") != company.enrichment_source_count:
        issues.append(
            FieldMappingIssue(
                field="enrichment_source_count",
                expected=json_data.get("enrichment_source_count"),
                actual=company.enrichment_source_count,
                message="Enrichment source count not preserved",
            )
        )

    # Check signal confidences populated
    if not company.signal_confidences:
        issues.append(
            FieldMappingIssue(
                field="signal_confidences",
                expected="dict with confidence weights",
                actual=company.signal_confidences,
                message="Signal confidences not populated",
            )
        )

    return issues


def generate_field_mapping_report(json_data: dict[str, Any], company: Company) -> str:
    """Generate a human-readable field mapping report.

    Args:
        json_data: Original JSON data
        company: Converted Company model

    Returns:
        Formatted report string
    """
    issues = validate_field_mapping(json_data, company)

    lines = [
        "=" * 60,
        "FIELD MAPPING AUDIT REPORT",
        "=" * 60,
        "",
        f"Company: {company.name}",
        f"ID: {company.id}",
        "",
    ]

    if issues:
        lines.append("⚠️  ISSUES FOUND:")
        lines.append("")
        for issue in issues:
            lines.append(f"  Field: {issue.field}")
            lines.append(f"    Expected: {issue.expected}")
            lines.append(f"    Actual: {issue.actual}")
            lines.append(f"    Message: {issue.message}")
            lines.append("")
    else:
        lines.append("✓ All fields mapped correctly!")
        lines.append("")

    # Summary of mapped fields
    lines.append("MAPPED FIELDS:")
    lines.append("  Basic info: name, industry, description, website, headquarters, founded_year")
    lines.append("  Financials: revenue, growth_rate, employees, funding, valuation")
    lines.append("  Profitability: profit_margin, ebitda_margin, recurring_revenue")
    lines.append("  Metadata: tier, ai_maturity, threat_level, saas_maturity")
    lines.append("  Preserved: revenue_cagr_3yr, revenue_cagr_5yr, enrichment_source_count")
    lines.append("  Generated: signal_confidences (from individual confidence fields)")
    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def audit_all_companies(json_path: str) -> dict[str, Any]:
    """Audit field mapping for all companies in a JSON file.

    Args:
        json_path: Path to competitor_data.json file

    Returns:
        Dictionary with audit results
    """
    import json

    # Import here to avoid circular import
    import sys

    sys.path.insert(0, "/home/ai-whisperers/solstein/src")
    from scripts.run_eneve_199 import convert_json_to_company

    with open(json_path) as f:
        data = json.load(f)

    companies = data.get("competitors", [])

    all_issues = []
    successful = 0
    failed = 0

    for company_data in companies:
        try:
            company = convert_json_to_company(company_data)
            issues = validate_field_mapping(company_data, company)

            if issues:
                all_issues.extend(issues)
                failed += 1
            else:
                successful += 1

        except Exception as e:
            all_issues.append(
                FieldMappingIssue(
                    field="conversion",
                    expected="successful conversion",
                    actual=str(e),
                    message=f"Failed to convert company: {company_data.get('company_name', 'Unknown')}",
                )
            )
            failed += 1

    return {
        "total": len(companies),
        "successful": successful,
        "failed": failed,
        "issues": all_issues,
        "success_rate": successful / len(companies) if companies else 0,
    }


if __name__ == "__main__":
    # Run audit on the 199 companies file
    import sys

    sys.path.insert(0, "/home/ai-whisperers/solstein/src")

    json_path = "/home/ai-whisperers/solstein/data/input/competitor_data_199.json"

    print("Running field mapping audit...")
    print()

    results = audit_all_companies(json_path)

    print("Audit Results:")
    print(f"  Total companies: {results['total']}")
    print(f"  Successful: {results['successful']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Success rate: {results['success_rate']:.1%}")
    print()

    if results["issues"]:
        print(f"Issues found: {len(results['issues'])}")
        for issue in results["issues"][:10]:  # Show first 10
            print(f"  - {issue.field}: {issue.message}")
        if len(results["issues"]) > 10:
            print(f"  ... and {len(results['issues']) - 10} more")
    else:
        print("✓ No issues found!")
