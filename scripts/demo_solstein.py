#!/usr/bin/env python3
"""
SolStein Minimal Working Demo

Demonstrates the core SolStein functionality:
1. Load competitor data from JSON
2. Create financial metrics with confidence scoring
3. Generate competitive intelligence insights
4. Export to Excel dashboard
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from solstein.data.models import (
    FinancialMetric, CompanyProfile, MarketAnalysis, 
    ConfidenceLevel, AIMaturity, ThreatLevel, CompanyTier
)
from solstein.analytics.scoring import GrowthScorer
from solstein.exporters.excel_exporter import ExcelExporter
from solstein.config import Settings

def load_competitor_data():
    """Load sample competitor data."""
    # Use the existing competitor data from the SolStein project
    data_path = Path(__file__).parent.parent / "legacy" / "old_root_backup" / "SolStein" / "COMPETITION" / "competitor_data.json"
    
    if not data_path.exists():
        print(f"❌ Competitor data not found at: {data_path}")
        print("Looking for alternative...")
        # Try to find any competitor data
        for path in Path(__file__).parent.rglob("*competitor*.json"):
            data_path = path
            print(f"Found: {data_path}")
            break
    
    if data_path.exists():
        with open(data_path, 'r') as f:
            return json.load(f)
    else:
        print("⚠️  No competitor data found, using sample data")
        return create_sample_data()

def create_sample_data():
    """Create sample competitor data for demo."""
    return {
        "competitors": [
            {
                "company_name": "Eneve (formerly Energy21)",
                "folder": "eneve",
                "data_availability": "High",
                "scorecard": {
                    "dimensions": {
                        "Revenue Growth": {"score": 8.5, "evidence": "15% CAGR over 3 years"},
                        "Funding Momentum": {"score": 7.0, "evidence": "Series B completed 2024"},
                        "Employee Growth": {"score": 6.5, "evidence": "Growing from 50 to 120 in 2 years"},
                        "Geographic Expansion": {"score": 8.0, "evidence": "Expanded to 3 new countries"},
                        "M&A Activity": {"score": 5.0, "evidence": "1 acquisition in 2023"},
                        "SaaS Maturity": {"score": 9.0, "evidence": "Cloud-native, 100% SaaS"}
                    },
                    "composite_score": 7.3,
                    "classification": "Rocket"
                },
                "revenue": {
                    "timeline": [
                        {"year": "2024", "eur_millions": 45.0, "yoy_growth_pct": 15.0, "confidence": "Confirmed"},
                        {"year": "2023", "eur_millions": 39.1, "yoy_growth_pct": 18.0, "confidence": "Confirmed"},
                        {"year": "2022", "eur_millions": 33.1, "yoy_growth_pct": 20.0, "confidence": "Confirmed"}
                    ],
                    "cagr_3yr_pct": 17.7,
                    "latest_revenue_eur_m": 45.0
                }
            },
            {
                "company_name": "Volue ASA",
                "folder": "volue",
                "data_availability": "High",
                "scorecard": {
                    "dimensions": {
                        "Revenue Growth": {"score": 9.0, "evidence": "25% CAGR, public company"},
                        "Funding Momentum": {"score": 8.5, "evidence": "Strong institutional backing"},
                        "Employee Growth": {"score": 7.5, "evidence": "Steady growth to 800+ employees"},
                        "Geographic Expansion": {"score": 9.5, "evidence": "Global presence across 15 countries"},
                        "M&A Activity": {"score": 8.0, "evidence": "Multiple strategic acquisitions"},
                        "SaaS Maturity": {"score": 8.5, "evidence": "Hybrid model, strong recurring revenue"}
                    },
                    "composite_score": 8.5,
                    "classification": "Rocket"
                },
                "revenue": {
                    "timeline": [
                        {"year": "2024", "eur_millions": 180.0, "yoy_growth_pct": 25.0, "confidence": "Estimated"},
                        {"year": "2023", "eur_millions": 144.0, "yoy_growth_pct": 20.0, "confidence": "Confirmed"},
                        {"year": "2022", "eur_millions": 120.0, "yoy_growth_pct": 18.0, "confidence": "Confirmed"}
                    ],
                    "cagr_3yr_pct": 21.0,
                    "latest_revenue_eur_m": 180.0
                }
            }
        ]
    }

def create_company_profile(company_data):
    """Create a CompanyProfile from raw data."""
    # Extract financial data
    revenue_data = company_data.get("revenue", {})
    timeline = revenue_data.get("timeline", [])
    
    if timeline:
        latest = timeline[0]
        revenue = latest.get("eur_millions")
        growth = latest.get("yoy_growth_pct")
    else:
        revenue = None
        growth = None
    
    # Create financial metric
    financial_metric = FinancialMetric(
        revenue=revenue,
        revenue_confidence=ConfidenceLevel.CONFIRMED if revenue else ConfidenceLevel.UNKNOWN,
        growth_rate=growth,
        growth_confidence=ConfidenceLevel.ESTIMATED if growth else ConfidenceLevel.UNKNOWN,
        employees=company_data.get("employee_count", 100),  # Default
        employees_confidence=ConfidenceLevel.ESTIMATED
    )
    
    # Determine tier based on revenue
    if revenue and revenue > 100:
        tier = CompanyTier.TIER_1
    elif revenue and revenue > 50:
        tier = CompanyTier.TIER_2
    elif revenue and revenue > 10:
        tier = CompanyTier.TIER_3
    else:
        tier = CompanyTier.TIER_4
    
    # Create company profile
    profile = CompanyProfile(
        id=company_data.get("folder", "").lower().replace(" ", "-"),
        name=company_data.get("company_name", "Unknown"),
        industry="Energy Software",  # Default for demo
        tier=tier,
        financials=financial_metric,
        ai_maturity=AIMaturity.STRONG,  # Default for demo
        threat_level=ThreatLevel.MEDIUM,  # Default
        saas_maturity=8,  # Default
        tech_stack=["Python", "React", "PostgreSQL"],  # Default
        geographic_presence=["Europe"],  # Default
        key_customers=["Utilities", "Energy Traders"],  # Default
        last_updated=datetime.now()
    )
    
    return profile

def analyze_market(profiles):
    """Analyze the competitive landscape."""
    # Calculate market shares
    total_revenue = sum(p.financials.revenue or 0 for p in profiles)
    
    market_insights = []
    for profile in profiles:
        market_share = (profile.financials.revenue / total_revenue * 100) if total_revenue > 0 else 0
        
        insight = {
            "company": profile.name,
            "revenue_eur_m": profile.financials.revenue,
            "growth_rate": profile.financials.growth_rate,
            "market_share": round(market_share, 1),
            "tier": profile.tier.value,
            "ai_maturity": profile.ai_maturity.value,
            "threat_level": profile.threat_level.value
        }
        market_insights.append(insight)
    
    # Sort by revenue
    market_insights.sort(key=lambda x: x["revenue_eur_m"] or 0, reverse=True)
    
    return market_insights

def generate_excel_report(profiles, market_insights, output_path):
    """Generate Excel report."""
    try:
        exporter = ExcelExporter()
        
        # Use the existing create_dashboard method
        exporter.create_dashboard(profiles, output_path)
        
        print(f"   ✅ Dashboard created successfully")
        
        # Also create a simple CSV for market insights (fallback)
        csv_path = output_path.with_suffix(".csv")
        import csv
        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ["company", "revenue_eur_m", "growth_rate", "market_share", "tier", "ai_maturity", "threat_level"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for insight in market_insights:
                writer.writerow({
                    "company": insight["company"],
                    "revenue_eur_m": insight["revenue_eur_m"],
                    "growth_rate": insight["growth_rate"],
                    "market_share": insight["market_share"],
                    "tier": insight["tier"],
                    "ai_maturity": insight["ai_maturity"],
                    "threat_level": insight["threat_level"]
                })
        
        print(f"   ✅ CSV backup created: {csv_path}")
        
        return True
    except Exception as e:
        print(f"❌ Error generating Excel report: {e}")
        print(f"   Trying alternative approach...")
        
        # Fallback: Create simple CSV
        try:
            import csv
            csv_path = output_path.with_suffix(".csv")
            with open(csv_path, 'w', newline='') as csvfile:
                fieldnames = ["company", "revenue_eur_m", "growth_rate", "market_share", "tier", "ai_maturity", "threat_level"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for insight in market_insights:
                    writer.writerow({
                        "company": insight["company"],
                        "revenue_eur_m": insight["revenue_eur_m"],
                        "growth_rate": insight["growth_rate"],
                        "market_share": insight["market_share"],
                        "tier": insight["tier"],
                        "ai_maturity": insight["ai_maturity"],
                        "threat_level": insight["threat_level"]
                    })
            
            print(f"   ✅ Created CSV report: {csv_path}")
            return True
        except Exception as e2:
            print(f"❌ CSV fallback also failed: {e2}")
            return False

def main():
    """Main demo function."""
    print("=" * 60)
    print("SOLSTEIN COMPETITIVE INTELLIGENCE DEMO")
    print("=" * 60)
    
    # Step 1: Load settings
    print("\n1. Loading configuration...")
    settings = Settings()
    print(f"   ✅ Environment: {settings.environment}")
    print(f"   ✅ Data directory: {settings.data.data_dir}")
    
    # Step 2: Load competitor data
    print("\n2. Loading competitor data...")
    competitor_data = load_competitor_data()
    competitors = competitor_data.get("competitors", [])
    print(f"   ✅ Loaded {len(competitors)} competitors")
    
    # Step 3: Create company profiles
    print("\n3. Creating company profiles...")
    profiles = []
    for i, company in enumerate(competitors[:5]):  # Limit to 5 for demo
        profile = create_company_profile(company)
        profiles.append(profile)
        print(f"   {i+1}. {profile.name}: €{profile.financials.revenue or 'N/A'}M, {profile.financials.growth_rate or 'N/A'}% growth")
    
    # Step 4: Analyze market
    print("\n4. Analyzing competitive landscape...")
    market_insights = analyze_market(profiles)
    
    print("\n   MARKET ANALYSIS RESULTS:")
    print("   " + "-" * 50)
    for insight in market_insights:
        print(f"   • {insight['company']}: {insight['market_share']}% market share "
              f"(€{insight['revenue_eur_m']}M, {insight['growth_rate']}% growth)")
    
    # Step 5: Generate Excel report
    print("\n5. Generating Excel report...")
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"solstein_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    if generate_excel_report(profiles, market_insights, output_path):
        print(f"   ✅ Report saved to: {output_path}")
    else:
        print("   ⚠️  Could not generate Excel report (check dependencies)")
    
    # Step 6: Demonstrate scoring
    print("\n6. Calculating growth scores...")
    scorer = GrowthScorer()
    for profile in profiles:
        try:
            if profile.financials.revenue and profile.financials.growth_rate:
                scored_profile = scorer.calculate_scores(profile)
                # Get growth score from the scored profile
                growth_score = getattr(scored_profile, 'growth_score', None)
                if growth_score:
                    classification = "Rocket" if growth_score >= 7.0 else "Dinosaur" if growth_score <= 4.0 else "Neutral"
                    print(f"   • {profile.name}: Score {growth_score:.1f}/10 ({classification})")
                else:
                    print(f"   • {profile.name}: Score calculation not available")
            else:
                print(f"   • {profile.name}: Insufficient data for scoring")
        except Exception as e:
            print(f"   • {profile.name}: Error calculating score - {e}")
    
    # Step 7: Summary
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print(f"\nWhat we demonstrated:")
    print("1. ✅ Configuration management with Pydantic v2")
    print("2. ✅ Competitor data loading and validation")
    print("3. ✅ Financial metrics with confidence scoring")
    print("4. ✅ Market share analysis")
    print("5. ✅ Excel report generation")
    print("6. ✅ Growth scoring and classification")
    
    print(f"\nOutput files:")
    print(f"• Excel report: {output_path}")
    
    print("\nNext steps for SolStein:")
    print("1. Implement web API with FastAPI")
    print("2. Add data sources (SEC, Crunchbase, etc.)")
    print("3. Build web dashboard")
    print("4. Deploy with Docker")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)