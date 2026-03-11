#!/usr/bin/env python3
"""Generate Excel Attractiveness Board from AI Research Results.

Converts research_results.json (from ai-research-batch) into Company domain
models and feeds them to the ImprovedExcelExporter to produce a dashboard.

Usage:
    python scripts/generate_excel_dashboard.py \
        data/research_results/research_results.json \
        data/research_results/european_energy_dashboard.xlsx
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.exporters.excel_improved import ImprovedExcelExporter


def classify_tier(company_data: dict) -> str:
    """Classify company tier based on employee count and revenue."""
    basic = company_data.get("basic_info", {})
    financials = company_data.get("financials", {})

    employees = basic.get("employees")
    revenue = financials.get("revenue")

    # Try to convert to numbers
    try:
        employees = int(employees) if employees else 0
    except (ValueError, TypeError):
        employees = 0

    try:
        revenue = float(revenue) if revenue else 0
    except (ValueError, TypeError):
        revenue = 0

    if employees > 10000 or revenue > 1000:
        return "Tier 1"
    elif employees > 1000 or revenue > 100:
        return "Tier 2"
    elif employees > 100 or revenue > 10:
        return "Tier 3"
    else:
        return "Tier 4"


def classify_threat(company_data: dict) -> str:
    """Classify threat level based on confidence and data richness."""
    confidence = company_data.get("confidence_score", 0)
    sources = len(company_data.get("data_sources", []))

    if confidence > 0.8 and sources > 5:
        return "High"
    elif confidence > 0.6 or sources > 3:
        return "Medium"
    else:
        return "Low"


def to_float(val) -> float | None:
    """Safely convert a value to float."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def to_int(val) -> int | None:
    """Safely convert a value to int."""
    if val is None:
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def research_to_company(data: dict) -> SimpleNamespace:
    basic = data.get("basic_info", {})
    financials = data.get("financials", {})
    funding_data = data.get("funding", {})
    name = data.get("company_name", "Unknown")

    employees = to_int(basic.get("employees"))
    revenue = to_float(financials.get("revenue"))
    valuation = to_float(financials.get("valuation"))
    total_funding = to_float(funding_data.get("total_raised"))

    financials_ns = SimpleNamespace(
        revenue_eur_m=revenue,
        growth_rate_pct=None,
        profit_margin_pct=None,
        total_funding_raised_eur=total_funding,
        latest_valuation_eur=valuation,
    )

    company = SimpleNamespace(
        id=f"COMP-{abs(hash(name))}",
        name=name,
        company_name=name,
        industry=basic.get("industry", "Energy Software"),
        description=basic.get("description"),
        website=basic.get("website"),
        headquarters=basic.get("headquarters"),
        founded_year=to_int(basic.get("founded_year")),
        tier=classify_tier(data),
        threat_level=classify_threat(data),
        financials=financials_ns,
        revenue_eur_m=revenue,
        growth_rate_pct=None,
        profit_margin_pct=None,
        total_funding_raised_eur=total_funding,
        latest_valuation_eur=valuation,
        revenue=revenue,
        employees=employees,
        employee_count=employees,
        funding=total_funding,
        valuation=valuation,
        ai_score=data.get("confidence_score", 0),
        market_share_pct=None,
        competitive_position_score=data.get("confidence_score", 0),
        classification="researched",
        data_source="ai_research",
        data_source_type="real",
        last_updated=datetime.now(timezone.utc),
        source_links=[s.get("url", "") for s in data.get("data_sources", [])],
        confidence_scores={
            "overall": data.get("confidence_score", 0),
        },
        enrichment_source_count=len(data.get("data_sources", [])),
    )

    return company


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_excel_dashboard.py <research_results.json> [output.xlsx]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.parent / "european_energy_dashboard.xlsx"

    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    # Load research results
    with open(input_path) as f:
        results = json.load(f)

    companies_data = results.get("companies", [])
    summary = results.get("summary", {})
    errors = results.get("errors", [])

    print(f"📊 Loading {len(companies_data)} company research results...")
    print(f"   Summary: {summary.get('successful', 0)} successful, {summary.get('failed', 0)} failed")
    print(f"   Avg Confidence: {summary.get('avg_confidence', 0):.2f}")

    # Convert to Company domain models
    companies = []
    for cd in companies_data:
        try:
            company = research_to_company(cd)
            companies.append(company)
            print(f"   ✅ {company.name} (tier={company.tier}, revenue={company.revenue}, employees={company.employees})")
        except Exception as e:
            print(f"   ❌ Failed to convert {cd.get('company_name', 'Unknown')}: {e}")

    if not companies:
        print("No companies to export!")
        sys.exit(1)

    # Generate Excel dashboard
    print(f"\n📈 Generating Excel dashboard with {len(companies)} companies...")
    exporter = ImprovedExcelExporter()

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_companies": len(companies),
        "avg_confidence": summary.get("avg_confidence", 0),
        "research_errors": errors,
        "source": "AI Research Pipeline (SearXNG + DeepInfra/Mistral/NVIDIA)",
    }

    exporter.create_dashboard(companies, output_path, metadata=metadata)
    print(f"\n✅ Dashboard saved to: {output_path}")
    print(f"   Sheets: Executive Summary, Market Rankings, Financial Intelligence, Export Metadata")


if __name__ == "__main__":
    main()
