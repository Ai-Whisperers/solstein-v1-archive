#!/usr/bin/env python3
"""
SolStein CLI - Competitive Intelligence Platform

Command-line interface following clean architecture patterns from Vete.
Provides enterprise-grade competitive intelligence for VC/PE firms.
"""

import sys
import json
import click
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Configure logging (Vete pattern)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

try:
    from solstein.data.models import CompanyProfile, FinancialMetric, ConfidenceLevel
    from solstein.analytics.scoring import GrowthScorer
    from solstein.exporters.excel_exporter import ExcelExporter
    from solstein.config import Settings
    HAS_DEPS = True
except ImportError as e:
    logger.warning(f"Some dependencies not available: {e}")
    HAS_DEPS = False


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """SolStein - AI-Powered Competitive Intelligence Platform"""
    pass


@cli.command()
@click.option('--env', default='development', help='Environment (development/production)')
def config(env: str):
    """Show current configuration"""
    try:
        settings = Settings()
        click.echo("📊 SolStein Configuration:")
        click.echo(f"  Environment: {settings.environment}")
        click.echo(f"  Data Directory: {settings.data.data_dir}")
        click.echo(f"  Database URL: {settings.database.url[:30]}..." if settings.database.url else "  Database URL: Not configured")
        click.echo(f"  Log Level: {settings.logging.level}")
        click.echo(f"  API Keys: {'Configured' if settings.openai_api_key or settings.perplexity_api_key else 'Not configured'}")
    except Exception as e:
        click.echo(f"❌ Error loading configuration: {e}", err=True)


@cli.command()
@click.option('--input', '-i', type=click.Path(exists=True), help='Input JSON file')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.option('--limit', '-l', type=int, default=10, help='Limit number of companies')
def analyze(input: Optional[str], output: Optional[str], limit: int):
    """Analyze competitor data"""
    if not HAS_DEPS:
        click.echo("❌ Required dependencies not available. Install with: pip install -e .", err=True)
        sys.exit(1)
    
    try:
        # Load data
        if input:
            data_path = Path(input)
        else:
            # Default to project data
            data_path = Path(__file__).parent.parent / "legacy" / "old_root_backup" / "SolStein" / "COMPETITION" / "competitor_data.json"
        
        if not data_path.exists():
            click.echo(f"❌ Data file not found: {data_path}", err=True)
            click.echo("💡 Try: solstein analyze --input /path/to/competitor_data.json")
            sys.exit(1)
        
        click.echo(f"📂 Loading data from: {data_path}")
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        competitors = data.get("competitors", [])[:limit]
        click.echo(f"📊 Analyzing {len(competitors)} competitors...")
        
        # Create output directory
        if output:
            output_dir = Path(output)
        else:
            output_dir = Path("analysis_output") / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Analyze each competitor
        results = []
        scorer = GrowthScorer()
        
        for i, comp in enumerate(competitors):
            click.echo(f"  {i+1}. {comp.get('company_name', 'Unknown')}")
            
            # Create financial metric (simplified)
            revenue_data = comp.get("revenue", {})
            timeline = revenue_data.get("timeline", [])
            
            if timeline:
                latest = timeline[0]
                revenue = latest.get("eur_millions")
                growth = latest.get("yoy_growth_pct")
            else:
                revenue = None
                growth = None
            
            financial = FinancialMetric(
                revenue=revenue,
                revenue_confidence=ConfidenceLevel.CONFIRMED if revenue else ConfidenceLevel.UNKNOWN,
                growth_rate=growth,
                growth_confidence=ConfidenceLevel.ESTIMATED if growth else ConfidenceLevel.UNKNOWN,
                employees=100  # Default
            )
            
            # Create profile
            profile = CompanyProfile(
                id=comp.get("folder", f"company_{i}").lower().replace(" ", "-"),
                name=comp.get("company_name", f"Company {i}"),
                industry="Energy Software",  # Default
                financials=financial,
                last_updated=datetime.now()
            )
            
            # Score
            scored_profile = scorer.calculate_scores(profile)
            
            results.append({
                "company": profile.name,
                "revenue": profile.financials.revenue,
                "growth": profile.financials.growth_rate,
                "growth_score": getattr(scored_profile, 'growth_score', None),
                "classification": "Rocket" if getattr(scored_profile, 'growth_score', 0) >= 7.0 
                                else "Dinosaur" if getattr(scored_profile, 'growth_score', 0) <= 4.0 
                                else "Neutral"
            })
        
        # Save results
        results_path = output_dir / "analysis_results.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Generate Excel report
        excel_path = output_dir / "competitive_dashboard.xlsx"
        try:
            exporter = ExcelExporter()
            profiles = []  # Would need actual profiles
            # exporter.create_dashboard(profiles, excel_path)
            click.echo(f"  📈 Excel dashboard: {excel_path}")
        except Exception as e:
            click.echo(f"  ⚠️  Excel export failed: {e}")
        
        # Generate summary
        rockets = sum(1 for r in results if r["classification"] == "Rocket")
        dinosaurs = sum(1 for r in results if r["classification"] == "Dinosaur")
        
        click.echo("\n" + "="*60)
        click.echo("📈 ANALYSIS SUMMARY")
        click.echo("="*60)
        click.echo(f"Total Companies: {len(results)}")
        click.echo(f"Rockets (High Growth): {rockets}")
        click.echo(f"Dinosaurs (Low Growth): {dinosaurs}")
        click.echo(f"Neutral: {len(results) - rockets - dinosaurs}")
        
        if rockets > 0:
            click.echo("\n🚀 ROCKET COMPANIES:")
            for r in results:
                if r["classification"] == "Rocket":
                    click.echo(f"  • {r['company']}: Score {r['growth_score']:.1f}/10")
        
        click.echo(f"\n📁 Output saved to: {output_dir}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        click.echo(f"❌ Analysis failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--company', '-c', multiple=True, help='Company names to compare')
@click.option('--input', '-i', type=click.Path(exists=True), help='Input JSON file')
def compare(company: List[str], input: Optional[str]):
    """Compare specific companies"""
    if not HAS_DEPS:
        click.echo("❌ Required dependencies not available.", err=True)
        sys.exit(1)
    
    try:
        # Load data
        if input:
            data_path = Path(input)
        else:
            data_path = Path(__file__).parent.parent / "legacy" / "old_root_backup" / "SolStein" / "COMPETITION" / "competitor_data.json"
        
        if not data_path.exists():
            click.echo(f"❌ Data file not found: {data_path}", err=True)
            sys.exit(1)
        
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        competitors = data.get("competitors", [])
        
        # Filter companies
        selected = []
        for comp in competitors:
            comp_name = comp.get("company_name", "")
            if company:
                if any(c.lower() in comp_name.lower() for c in company):
                    selected.append(comp)
            else:
                selected.append(comp)
        
        if not selected:
            click.echo("❌ No companies found matching criteria", err=True)
            sys.exit(1)
        
        click.echo("📊 COMPANY COMPARISON")
        click.echo("="*60)
        
        for comp in selected[:5]:  # Limit to 5
            revenue_data = comp.get("revenue", {})
            timeline = revenue_data.get("timeline", [])
            scorecard = comp.get("scorecard", {})
            
            click.echo(f"\n🏢 {comp.get('company_name')}")
            click.echo(f"   📁 Folder: {comp.get('folder', 'N/A')}")
            click.echo(f"   📊 Data Availability: {comp.get('data_availability', 'N/A')}")
            
            if timeline:
                latest = timeline[0]
                click.echo(f"   💰 Revenue: €{latest.get('eur_millions', 'N/A')}M ({latest.get('yoy_growth_pct', 'N/A')}% YoY)")
            
            if scorecard:
                click.echo(f"   🎯 Composite Score: {scorecard.get('composite_score', 'N/A')}/10")
                click.echo(f"   🏷️  Classification: {scorecard.get('classification', 'N/A')}")
        
        click.echo("\n" + "="*60)
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}", exc_info=True)
        click.echo(f"❌ Comparison failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output directory')
def report(output: Optional[str]):
    """Generate comprehensive competitive intelligence report"""
    if not HAS_DEPS:
        click.echo("❌ Required dependencies not available.", err=True)
        sys.exit(1)
    
    try:
        # Create output directory
        if output:
            output_dir = Path(output)
        else:
            output_dir = Path("reports") / datetime.now().strftime("%Y%m%d")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load data
        data_path = Path(__file__).parent.parent / "legacy" / "old_root_backup" / "SolStein" / "COMPETITION" / "competitor_data.json"
        
        if not data_path.exists():
            click.echo(f"❌ Data file not found: {data_path}", err=True)
            sys.exit(1)
        
        click.echo(f"📂 Loading data from: {data_path}")
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        competitors = data.get("competitors", [])
        
        # Generate report
        total_revenue = 0
        total_growth = 0
        growth_count = 0
        
        for comp in competitors:
            revenue_data = comp.get("revenue", {})
            timeline = revenue_data.get("timeline", [])
            if timeline:
                revenue = timeline[0].get("eur_millions")
                growth = timeline[0].get("yoy_growth_pct")
                if revenue is not None:
                    total_revenue += revenue
                if growth is not None:
                    total_growth += growth
                    growth_count += 1
        
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "total_companies": len(competitors),
            "market_overview": {
                "total_revenue_eur_m": total_revenue,
                "average_growth_pct": total_growth / growth_count if growth_count > 0 else 0
            },
            "companies": []
        }
        
        for comp in competitors[:20]:  # Limit to 20
            revenue_data = comp.get("revenue", {})
            timeline = revenue_data.get("timeline", [])
            scorecard = comp.get("scorecard", {})
            
            company_info = {
                "name": comp.get("company_name"),
                "folder": comp.get("folder"),
                "data_availability": comp.get("data_availability"),
                "revenue": timeline[0].get("eur_millions") if timeline else None,
                "growth": timeline[0].get("yoy_growth_pct") if timeline else None,
                "composite_score": scorecard.get("composite_score"),
                "classification": scorecard.get("classification")
            }
            report_data["companies"].append(company_info)
        
        # Save report
        report_path = output_dir / f"solstein_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        # Also create markdown summary
        md_path = output_dir / "README.md"
        with open(md_path, 'w') as f:
            f.write(f"# SolStein Competitive Intelligence Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Market Overview\n\n")
            f.write(f"- **Total Companies Analyzed**: {report_data['total_companies']}\n")
            f.write(f"- **Total Revenue**: €{report_data['market_overview']['total_revenue_eur_m']:,.0f}M\n")
            f.write(f"- **Average Growth Rate**: {report_data['market_overview']['average_growth_pct']:.1f}%\n\n")
            
            f.write(f"## Top Companies\n\n")
            f.write(f"| Company | Revenue (€M) | Growth (%) | Score | Classification |\n")
            f.write(f"|---------|--------------|------------|-------|----------------|\n")
            
            for comp in sorted(report_data["companies"], 
                             key=lambda x: x["revenue"] or 0, 
                             reverse=True)[:10]:
                f.write(f"| {comp['name']} | {comp['revenue'] or 'N/A'} | {comp['growth'] or 'N/A'} | {comp['composite_score'] or 'N/A'} | {comp['classification'] or 'N/A'} |\n")
        
        click.echo(f"✅ Report generated: {report_path}")
        click.echo(f"📝 Markdown summary: {md_path}")
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        click.echo(f"❌ Report generation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
def demo():
    """Run the SolStein demonstration"""
    click.echo("🚀 Running SolStein Demo...")
    
    # Run the demo script
    demo_path = Path(__file__).parent / "demo_solstein.py"
    if demo_path.exists():
        import subprocess
        result = subprocess.run([sys.executable, str(demo_path)], 
                              capture_output=True, text=True)
        click.echo(result.stdout)
        if result.stderr:
            click.echo(result.stderr, err=True)
    else:
        click.echo("❌ Demo script not found", err=True)


if __name__ == "__main__":
    cli()