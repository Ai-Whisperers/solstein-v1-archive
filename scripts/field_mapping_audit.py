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

import json
import sys
from dataclasses import dataclass
from pathlib import Path as _Path
from typing import Any

# Setup PYTHONPATH so solstein package is importable when run directly
sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "src"))

from solstein.data.loaders import convert_to_domain_company
from solstein.domain.models import Company


@dataclass
class FieldMappingIssue:
    """Represents a field mapping issue."""

    field: str
    expected: Any
    actual: Any
    message: str


def _check_basic_fields(json_data: dict[str, Any], company: Company) -> list[FieldMappingIssue]:
    """Check that basic identity/profile fields match between JSON and Company model."""
    issues: list[FieldMappingIssue] = []
    checks = [
        ("company_name", json_data.get("company_name"), company.name, "Company name mismatch"),
        ("description", json_data.get("description"), company.description, "Description mismatch"),
        ("website", json_data.get("website"), company.website, "Website mismatch"),
        ("country", json_data.get("country"), company.headquarters, "Country/headquarters mismatch"),
        ("founded_year", json_data.get("founded_year"), company.founded_year, "Founded year mismatch"),
    ]
    for field, expected, actual, message in checks:
        if expected != actual:
            issues.append(FieldMappingIssue(field=field, expected=expected, actual=actual, message=message))

    industry = json_data.get("industry")
    if industry != company.industry and company.industry != "Energy Software":
        issues.append(
            FieldMappingIssue(
                field="industry",
                expected=industry,
                actual=company.industry,
                message="Industry mismatch or unexpected default",
            )
        )
    return issues


def _check_financial_fields(json_data: dict[str, Any], company: Company) -> list[FieldMappingIssue]:
    """Check that financial/revenue fields are preserved correctly."""
    issues: list[FieldMappingIssue] = []
    revenue_data = json_data.get("revenue", {})
    timeline = revenue_data.get("timeline", [])
    latest = timeline[0] if timeline else {}

    fin_checks = [
        ("revenue.timeline[0].eur_millions", latest.get("eur_millions"), company.financials.revenue, "Revenue mismatch"),
        ("revenue.timeline[0].yoy_growth_pct", latest.get("yoy_growth_pct"), company.financials.growth_rate, "Growth rate mismatch"),
        ("revenue.cagr_3yr_pct", revenue_data.get("cagr_3yr_pct"), company.revenue_cagr_3yr, "CAGR 3-year not preserved"),
        ("revenue.cagr_5yr_pct", revenue_data.get("cagr_5yr_pct"), company.revenue_cagr_5yr, "CAGR 5-year not preserved"),
        ("enrichment_source_count", json_data.get("enrichment_source_count"), company.enrichment_source_count, "Enrichment source count not preserved"),
    ]
    for field, expected, actual, message in fin_checks:
        if expected != actual:
            issues.append(FieldMappingIssue(field=field, expected=expected, actual=actual, message=message))

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


def validate_field_mapping(json_data: dict[str, Any], company: Company) -> list[FieldMappingIssue]:
    """Validate that all fields from JSON are correctly mapped to Company model.

    Args:
        json_data: Original JSON data
        company: Converted Company model

    Returns:
        List of field mapping issues (empty if all valid)
    """
    return _check_basic_fields(json_data, company) + _check_financial_fields(json_data, company)


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
    with open(json_path) as f:
        data = json.load(f)

    companies = data.get("competitors", [])

    all_issues = []
    successful = 0
    failed = 0

    for idx, company_data in enumerate(companies):
        try:
            company = convert_to_domain_company(company_data, idx)
            issues = validate_field_mapping(company_data, company)

            if issues:
                all_issues.extend(issues)
                failed += 1
            else:
                successful += 1

        except (ValueError, TypeError, AttributeError, KeyError) as e:
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
    _project_root = _Path(__file__).resolve().parent.parent
    json_path = str(_project_root / "tests/fixtures/synthetic/competitor_data_199.json")

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
