#!/usr/bin/env python3
"""
Task 1: Data Source Audit and Quality Report
Comprehensive analysis of all 199 companies to identify NULL values, data completeness, and source lineage.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.data.loaders import CompetitorDataLoader


def audit_data_quality() -> dict[str, Any]:
    """
    Audit all 199 companies for data quality and completeness.

    Returns:
        Dictionary with audit results including completeness percentages,
        data quality tiers, and top/bottom companies.
    """

    print("🔍 Starting Data Quality Audit...")
    print("=" * 80)

    # Load all companies
    loader = CompetitorDataLoader()
    companies = loader.load_companies()
    print(f"✅ Loaded {len(companies)} companies from competitor_data.json")

    # Define fields to audit
    fields_to_audit = [
        "revenue",
        "growth_rate",
        "employees",
        "profit_margin",
        "funding_raised",
        "valuation",
        "ai_score",
        "ebitda_margin",
        "recurring_revenue_pct",
        "revenue_per_employee_eur_k",
        "employee_cagr_3yr",
        "open_positions",
        "ai_signal_level",
        "ai_key_capabilities",
        "ai_in_production",
    ]

    # Track completeness per field
    field_completeness = defaultdict(lambda: {"total": 0, "null": 0, "complete": 0})
    company_completeness = {}

    print(f"\n📊 Analyzing {len(fields_to_audit)} fields across {len(companies)} companies...")

    # Audit each company
    for company in companies:
        company_id = company.id
        complete_fields = 0
        total_fields = len(fields_to_audit)

        for field in fields_to_audit:
            field_completeness[field]["total"] += 1

            # Get value from company
            value = None
            if field == "revenue":
                value = company.financials.revenue if company.financials else None
            elif field == "growth_rate":
                value = company.financials.growth_rate if company.financials else None
            elif field == "employees":
                value = company.financials.employees if company.financials else None
            elif field == "profit_margin":
                value = company.profit_margin
            elif field == "funding_raised":
                value = company.total_funding_raised_eur
            elif field == "valuation":
                value = company.latest_valuation_eur
            elif field == "ai_score":
                value = company.ai_score
            elif field == "ebitda_margin":
                value = company.ebitda_margin
            elif field == "recurring_revenue_pct":
                value = company.recurring_revenue_pct
            elif field == "revenue_per_employee_eur_k":
                value = company.revenue_per_employee_eur_k
            elif field == "employee_cagr_3yr":
                value = company.employee_cagr_3yr
            elif field == "open_positions":
                value = company.open_positions
            elif field == "ai_signal_level":
                value = company.ai_signal_level
            elif field == "ai_key_capabilities":
                value = company.ai_key_capabilities
            elif field == "ai_in_production":
                value = company.ai_in_production

            # Check if value is present
            if value is None or (isinstance(value, str) and value.lower() == "unknown"):
                field_completeness[field]["null"] += 1
            else:
                field_completeness[field]["complete"] += 1
                complete_fields += 1

        # Calculate company completeness percentage
        completeness_pct = (complete_fields / total_fields * 100) if total_fields > 0 else 0

        # Determine data quality tier
        if completeness_pct >= 90:
            tier = "COMPLETE"
        elif completeness_pct >= 50:
            tier = "PARTIAL"
        elif completeness_pct >= 10:
            tier = "MINIMAL"
        else:
            tier = "INSUFFICIENT"

        company_completeness[company_id] = {
            "name": company.name,
            "completeness_pct": round(completeness_pct, 2),
            "complete_fields": complete_fields,
            "total_fields": total_fields,
            "tier": tier,
            "revenue": company.financials.revenue if company.financials else None,
            "employees": company.financials.employees if company.financials else None,
        }

    # Calculate field completeness percentages
    completeness_percentages = {}
    for field, counts in field_completeness.items():
        pct = (counts["complete"] / counts["total"] * 100) if counts["total"] > 0 else 0
        completeness_percentages[field] = {
            "completeness_pct": round(pct, 2),
            "complete": counts["complete"],
            "null": counts["null"],
            "total": counts["total"],
        }

    # Find top 10 most complete companies
    sorted_companies = sorted(company_completeness.items(), key=lambda x: x[1]["completeness_pct"], reverse=True)
    top_10_complete = sorted_companies[:10]
    top_10_incomplete = sorted_companies[-10:]

    # Count tier distribution
    tier_distribution = defaultdict(int)
    for company_data in company_completeness.values():
        tier_distribution[company_data["tier"]] += 1

    # Build audit report
    audit_report = {
        "audit_date": "2026-02-25",
        "companies_analyzed": len(companies),
        "fields_analyzed": fields_to_audit,
        "completeness_percentages": completeness_percentages,
        "tier_distribution": dict(tier_distribution),
        "top_10_most_complete": [
            {
                "rank": i + 1,
                "company_id": company_id,
                "company_name": company_data["name"],
                "completeness_pct": company_data["completeness_pct"],
                "complete_fields": company_data["complete_fields"],
                "tier": company_data["tier"],
            }
            for i, (company_id, company_data) in enumerate(top_10_complete)
        ],
        "top_10_least_complete": [
            {
                "rank": i + 1,
                "company_id": company_id,
                "company_name": company_data["name"],
                "completeness_pct": company_data["completeness_pct"],
                "complete_fields": company_data["complete_fields"],
                "tier": company_data["tier"],
            }
            for i, (company_id, company_data) in enumerate(top_10_incomplete)
        ],
        "all_companies": company_completeness,
    }

    return audit_report


def print_summary(audit_report: dict[str, Any]) -> None:
    """Print audit summary to console."""

    print("\n" + "=" * 80)
    print("📋 DATA QUALITY AUDIT SUMMARY")
    print("=" * 80)

    print(f"\n✅ Companies Analyzed: {audit_report['companies_analyzed']}")
    print(f"📊 Fields Analyzed: {len(audit_report['fields_analyzed'])}")

    print("\n📈 Field Completeness:")
    for field, data in sorted(
        audit_report["completeness_percentages"].items(), key=lambda x: x[1]["completeness_pct"], reverse=True
    ):
        pct = data["completeness_pct"]
        complete = data["complete"]
        total = data["total"]
        null_count = data["null"]
        print(f"  {field:30s}: {pct:6.1f}% ({complete:3d}/{total:3d} complete, {null_count:3d} NULL)")

    print("\n🏆 Data Quality Tier Distribution:")
    for tier, count in sorted(audit_report["tier_distribution"].items()):
        pct = count / audit_report["companies_analyzed"] * 100
        print(f"  {tier:15s}: {count:3d} companies ({pct:5.1f}%)")

    print("\n🥇 Top 10 Most Complete Companies:")
    for item in audit_report["top_10_most_complete"]:
        print(f"  {item['rank']:2d}. {item['company_name']:40s} {item['completeness_pct']:6.1f}% ({item['tier']})")

    print("\n🥉 Top 10 Least Complete Companies:")
    for item in audit_report["top_10_least_complete"]:
        print(f"  {item['rank']:2d}. {item['company_name']:40s} {item['completeness_pct']:6.1f}% ({item['tier']})")

    print("\n" + "=" * 80)


def main():
    """Main entry point."""

    try:
        # Run audit
        audit_report = audit_data_quality()

        # Print summary
        print_summary(audit_report)

        # Save report
        output_path = Path(__file__).parent.parent / "data" / "output" / "data_quality_audit.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(audit_report, f, indent=2, default=str)

        print(f"\n✅ Audit report saved to: {output_path}")
        print(f"📊 Total file size: {output_path.stat().st_size / 1024:.1f} KB")

        return 0

    except Exception as e:
        print(f"\n❌ Error during audit: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
