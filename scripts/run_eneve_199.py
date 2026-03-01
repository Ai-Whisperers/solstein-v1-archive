#!/usr/bin/env python3
"""
Run ENEVE workflow with 199 companies.
Converts JSON data to Company models and generates outputs.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

# Setup paths
import sys
sys.path.insert(0, '/home/ai-whisperers/solstein/src')

from solstein.domain.models import Company, FinancialMetric, CompanyTier, AIMaturity, ThreatLevel, ConfidenceLevel
from solstein.analytics.scoring import GrowthScorer
from solstein.exporters.excel import ExcelExporter


def convert_json_to_company(data: dict) -> Company:
    """Convert competitor_data.json format to Company model."""
    # Extract revenue data from timeline
    revenue_timeline = data.get("revenue", {}).get("timeline", [])
    latest_revenue = revenue_timeline[0] if revenue_timeline else {}
    
    revenue = latest_revenue.get("eur_millions")
    growth_rate = latest_revenue.get("yoy_growth_pct")
    
    # Get confidence from timeline entry
    confidence_map = {
        "high": ConfidenceLevel.CONFIRMED,
        "medium": ConfidenceLevel.ESTIMATED,
        "low": ConfidenceLevel.UNKNOWN
    }
    revenue_confidence = confidence_map.get(latest_revenue.get("confidence", ""), ConfidenceLevel.UNKNOWN)
    
    # Extract employees (direct field, not nested)
    employees = data.get("employees")
    
    # Extract funding (direct field)
    funding_raised = data.get("funding_raised")
    
    # Extract valuation (direct field)
    valuation = data.get("valuation")
    
    # Extract AI maturity (direct field)
    ai_maturity_str = data.get("ai_maturity", "None")
    ai_maturity_map = {
        "Very Strong": AIMaturity.VERY_STRONG,
        "Strong": AIMaturity.STRONG,
        "Moderate": AIMaturity.MODERATE,
        "Low": AIMaturity.LOW,
        "None": AIMaturity.NONE
    }
    ai_maturity = ai_maturity_map.get(ai_maturity_str, AIMaturity.NONE)
    
    # Extract tier (use classification to infer)
    # FIXED: Phoenix -> Tier 1 (best), Salt -> Tier 2, Lead -> Tier 4 (worst)
    classification = data.get("classification", "Salt")
    tier_map = {
        "Phoenix": CompanyTier.TIER_1,  # Best companies get best tier
        "Salt": CompanyTier.TIER_2,     # Moderate companies
        "Lead": CompanyTier.TIER_4      # Struggling companies
    }
    tier = tier_map.get(classification, CompanyTier.TIER_3)
    
    # Build Company object
    return Company(
        id=data.get("company_name", "unknown").lower().replace(" ", "-").replace(".", ""),
        name=data.get("company_name", "Unknown"),
        industry=data.get("industry", "Energy Software"),
        description=data.get("description"),
        website=data.get("website"),
        headquarters=data.get("country"),
        founded_year=data.get("founded_year"),
        tier=tier,
        threat_level=ThreatLevel.LOW,
        ai_maturity=ai_maturity,
        saas_maturity=5,  # Default mid-range
        tech_stack=[],
        financials=FinancialMetric(
            revenue=revenue,
            revenue_confidence=revenue_confidence,
            growth_rate=growth_rate,
            growth_confidence=revenue_confidence,
            employees=employees,
            employees_confidence=ConfidenceLevel.UNKNOWN,
            funding_raised=funding_raised,
            funding_confidence=ConfidenceLevel.UNKNOWN,
            valuation=valuation,
            valuation_confidence=ConfidenceLevel.UNKNOWN
        ),
        geographic_presence=data.get("geographic_presence", []),
        key_customers=[],
        data_source="Solstein Competitive Intelligence",
        last_updated=datetime.now(timezone.utc)
    )


def main():
    print("=" * 60)
    print("ENEVE 199-Company Workflow")
    print("=" * 60)
    
    # Load 199 companies
    input_path = Path("data/input/competitor_data_199.json")
    with open(input_path) as f:
        data = json.load(f)
    
    companies_raw = data["competitors"]
    print(f"\n📊 Loaded {len(companies_raw)} companies from {input_path}")
    
    # Convert to Company models
    print("\n🔄 Converting to Company models...")
    companies = []
    errors = []
    for i, raw in enumerate(companies_raw):
        try:
            company = convert_json_to_company(raw)
            companies.append(company)
            if i < 3:
                print(f"  ✓ {company.name}: revenue={company.financials.revenue}M, growth={company.financials.growth_rate}%")
        except Exception as e:
            errors.append((raw.get("company_name", "Unknown"), str(e)))
            if len(errors) <= 5:
                print(f"  ✗ Error converting {raw.get('company_name', 'Unknown')}: {e}")
    
    if errors:
        print(f"\n⚠️  {len(errors)} conversion errors (showing first 5)")
    
    print(f"\n✅ Successfully converted {len(companies)} companies")
    
    # Score companies
    print("\n🎯 Scoring companies...")
    scorer = GrowthScorer()
    scored = []
    score_errors = []
    
    for company in companies:
        try:
            scored_company = scorer.calculate_scores(company)
            scored.append(scored_company)
        except Exception as e:
            score_errors.append((company.name, str(e)))
    
    print(f"✅ Successfully scored {len(scored)} companies")
    if score_errors:
        print(f"⚠️  {len(score_errors)} scoring errors")
    
    # Show sample results
    print("\n📈 Sample Results:")
    for company in scored[:5]:
        print(f"  {company.name}: composite={company.composite_score:.2f}, classification={company.classification}")
    
    # Save scored output
    output_dir = Path("data/output/exports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scored_path = output_dir / "eneve_full_199_scored.json"
    with open(scored_path, "w") as f:
        json.dump([c.model_dump(mode="json") for c in scored], f, indent=2)
    print(f"\n💾 Saved scored data to {scored_path}")
    
    # Create Excel dashboard
    print("\n📊 Creating Excel dashboard...")
    try:
        ExcelExporter().create_dashboard(scored, output_dir / "eneve_full_199_dashboard.xlsx")
        print(f"✅ Created Excel dashboard")
    except Exception as e:
        print(f"✗ Error creating Excel dashboard: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    phoenix_count = sum(1 for c in scored if c.classification == "Phoenix")
    salt_count = sum(1 for c in scored if c.classification == "Salt")
    lead_count = sum(1 for c in scored if c.classification == "Lead")
    
    avg_score = sum(c.composite_score for c in scored) / len(scored) if scored else 0
    
    print(f"Total Companies: {len(scored)}")
    print(f"Average Composite Score: {avg_score:.2f}")
    print(f"Phoenix (≥7.0): {phoenix_count}")
    print(f"Salt (4.0-7.0): {salt_count}")
    print(f"Lead (≤4.0): {lead_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
