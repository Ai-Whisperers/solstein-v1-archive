"""
Command-line interface for SolStein.
"""

import json
from pathlib import Path

import click
from loguru import logger

from .analytics.scoring import GrowthScorer
from .domain.models import Company, MarketAnalysis
from .exporters.excel import ExcelExporter
from .exporters.markdown.generator import ClientReportGenerator
from .extractors.markdown_extractor import BatchExtractor


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool) -> None:
    """SolStein - AI-Powered Competitive Intelligence Platform"""
    if verbose:
        logger.remove()
        logger.add(lambda msg: click.echo(msg, err=True), level="DEBUG")
    else:
        logger.remove()
        logger.add(lambda msg: click.echo(msg, err=True), level="INFO")


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output JSON file"
)
@click.option("--pattern", "-p", default="*.md", help="File pattern to match")
def extract(input_dir: Path, output: Path | None, pattern: str) -> None:
    """Extract data from markdown files."""
    click.echo(f"🔍 Extracting data from {input_dir}")

    extractor = BatchExtractor()
    profiles: list[Company] = extractor.extract_directory(input_dir, pattern)

    if not profiles:
        click.echo("❌ No profiles extracted", err=True)
        return

    click.echo(f"✅ Extracted {len(profiles)} profiles")

    if output:
        extractor.save_to_json(profiles, output)
        click.echo(f"💾 Saved to {output}")
    else:
        # Print summary
        for profile in profiles[:5]:  # Show first 5
            click.echo(f"  • {profile.name} ({profile.id})")
        if len(profiles) > 5:
            click.echo(f"  ... and {len(profiles) - 5} more")


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.argument("output_file", type=click.Path(path_type=Path))
@click.option(
    "--template", "-t", type=click.Path(exists=True), help="Excel template file"
)
def export_excel(input_file: Path, output_file: Path, template: Path | None) -> None:
    """Export data to Excel dashboard."""
    click.echo(f"📊 Exporting to Excel: {output_file}")

    try:
        # Load profiles from JSON
        data = json.loads(input_file.read_text())
        domain_companies = [Company(**item) for item in data]

        # Create exporter and generate dashboard
        exporter = ExcelExporter(template_path=template)
        exporter.create_dashboard(domain_companies, output_file)

        click.echo(f"✅ Dashboard created: {output_file}")
    except Exception as e:
        click.echo(f"❌ Failed to create dashboard: {e}", err=True)
        raise click.Abort() from e


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output file for scores"
)
def score(input_file: Path, output: Path | None) -> None:
    """Calculate growth and competitive scores."""
    click.echo("📈 Calculating scores...")

    try:
        # Load profiles
        data = json.loads(input_file.read_text())
        domain_companies = [Company(**item) for item in data]

        # Calculate scores
        scorer = GrowthScorer()
        scored_companies = []

        for company in domain_companies:
            scored_company = scorer.calculate_scores(company)
            scored_companies.append(scored_company)

            # Show summary
            click.echo(f"  • {company.name}:")
            # Handle None scores
            growth = scored_company.growth_score or 0.0
            health = scored_company.financial_health_score or 0.0
            pos = scored_company.competitive_position_score or 0.0

            click.echo(f"    Growth: {growth:.1f}/10")
            click.echo(f"    Financial Health: {health:.1f}/10")
            click.echo(f"    Competitive Position: {pos:.1f}/10")

        if output:
            # Save scored profiles
            output_data = [c.model_dump(mode="json") for c in scored_companies]
            output.write_text(json.dumps(output_data, indent=2, default=str))
            click.echo(f"💾 Saved scored profiles to {output}")

    except Exception as e:
        click.echo(f"❌ Failed to calculate scores: {e}", err=True)
        raise click.Abort() from e


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--market-name", "-n", default="Competitive Landscape", help="Market name"
)
def analyze_market(input_file: Path, market_name: str) -> None:
    """Create market-level analysis."""
    click.echo(f"🌍 Analyzing market: {market_name}")

    try:
        # Load profiles
        data = json.loads(input_file.read_text())
        domain_companies = [Company(**item) for item in data]

        # Re-using domain_companies for MarketAnalysis model
        analysis = MarketAnalysis(market_name=market_name, companies=domain_companies)

        # Show analysis
        click.echo("📊 Market Analysis:")
        click.echo(f"  Companies: {analysis.company_count}")
        # average_growth_rate property exists on MarketAnalysis
        avg_growth = analysis.average_growth_rate or 0.0
        click.echo(f"  Average Growth: {avg_growth:.1f}%")
        click.echo(f"  Market Leaders: {len(analysis.market_leaders)}")

        for leader in analysis.market_leaders:
            click.echo(f"    • {leader.name} (Tier {leader.tier})")

    except Exception as e:
        click.echo(f"❌ Failed to analyze market: {e}", err=True)
        raise click.Abort() from e


@cli.command()
@click.argument("profile1", type=str)
@click.argument("profile2", type=str)
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def compare(profile1: str, profile2: str, input_file: Path) -> None:
    """Compare two companies."""
    click.echo(f"⚖️ Comparing {profile1} vs {profile2}")

    try:
        # Load profiles
        data = json.loads(input_file.read_text())
        profiles = {p["id"]: Company(**p) for p in data}

        if profile1 not in profiles:
            click.echo(f"❌ Profile not found: {profile1}", err=True)
            return
        if profile2 not in profiles:
            click.echo(f"❌ Profile not found: {profile2}", err=True)
            return

        p1 = profiles[profile1]
        p2 = profiles[profile2]

        # Show comparison
        click.echo(f"\n{p1.name} vs {p2.name}:")
        click.echo(f"{'Metric':<20} {p1.name:<20} {p2.name:<20}")
        click.echo("-" * 60)

        metrics = [
            ("Revenue", p1.financials.revenue, p2.financials.revenue, "€"),
            ("Growth Rate", p1.financials.growth_rate, p2.financials.growth_rate, "%"),
            ("Employees", p1.financials.employees, p2.financials.employees, ""),
            ("AI Maturity", p1.ai_maturity, p2.ai_maturity, ""),
            ("Threat Level", p1.threat_level, p2.threat_level, ""),
        ]

        for name, v1, v2, unit in metrics:
            v1_str = f"{v1}{unit}" if v1 is not None else "N/A"
            v2_str = f"{v2}{unit}" if v2 is not None else "N/A"
            click.echo(f"{name:<20} {v1_str:<20} {v2_str:<20}")

    except Exception as e:
        click.echo(f"❌ Failed to compare profiles: {e}", err=True)
        raise click.Abort() from e


@cli.command()
@click.argument("company_name", type=str)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for reports",
)
def generate_report(company_name: str, output: Path | None) -> None:
    """Generate intelligence report for a company."""
    from .data.loaders import CompetitorDataLoader

    click.echo(f"📊 Generating reports for: {company_name}")

    try:
        loader = CompetitorDataLoader()
        companies = loader.load_companies()

        scorer = GrowthScorer()
        scored_companies = []
        for company in companies:
            scored = scorer.calculate_scores(company)
            scored_companies.append(scored)

        # Find target company
        target = None
        for c in scored_companies:
            if company_name.lower() in c.name.lower():
                target = c
                break

        if not target:
            click.echo(f"❌ Company not found: {company_name}", err=True)
            click.echo(
                f"Available companies: {', '.join([c.name for c in scored_companies[:10]])}..."
            )
            return

        # Get competitors (all other companies)
        competitors = [c for c in scored_companies if c.id != target.id]

        # Generate reports
        output_dir = output or Path(f"data/output/reports/{target.id}")
        generator = ClientReportGenerator(output_dir=output_dir)

        reports = generator.generate_client_report(target, competitors)

        click.echo(f"✅ Reports generated in: {output_dir}")
        click.echo(f"   - corporate-history.md")
        click.echo(f"   - deep-analysis.md")
        click.echo(f"   - financial-growth.md")
        click.echo(f"   - competitive-analysis.md")
        click.echo(f"   - market-overview.md")

    except Exception as e:
        click.echo(f"❌ Failed to generate report: {e}", err=True)
        raise click.Abort() from e


@cli.command()
@click.argument("company_name", type=str)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for reports",
)
@click.option("--no-llm", is_flag=True, help="Disable LLM enhancements")
def generate_llm_report(company_name: str, output: Path | None, no_llm: bool) -> None:
    """Generate LLM-enhanced intelligence report for a company."""
    from .data.loaders import CompetitorDataLoader

    click.echo(f"🤖 Generating LLM-enhanced reports for: {company_name}")

    try:
        loader = CompetitorDataLoader()
        companies = loader.load_companies()

        scorer = GrowthScorer()
        scored_companies = []
        for company in companies:
            scored = scorer.calculate_scores(company)
            scored_companies.append(scored)

        target = None
        for c in scored_companies:
            if company_name.lower() in c.name.lower():
                target = c
                break

        if not target:
            click.echo(f"❌ Company not found: {company_name}", err=True)
            click.echo(
                f"Available: {', '.join([c.name for c in scored_companies[:10]])}..."
            )
            return

        competitors = [c for c in scored_companies if c.id != target.id]

        output_dir = output or Path(f"data/output/reports/llm/{target.id}")

        if no_llm:
            from .exporters.report_generator import ClientReportGenerator

            generator = ClientReportGenerator(output_dir=output_dir, use_llm=False)
            reports = generator.generate_client_report(target, competitors)
        else:
            from .exporters.report_generator import LLMEnhancedReportGenerator
            import asyncio

            generator = LLMEnhancedReportGenerator(output_dir=output_dir, use_llm=True)
            reports = asyncio.run(
                generator.generate_llm_enhanced_report(target, competitors)
            )

        click.echo(f"✅ LLM-enhanced reports generated in: {output_dir}")
        for name in reports:
            click.echo(f"   - {name}")

    except Exception as e:
        click.echo(f"❌ Failed to generate LLM report: {e}", err=True)
        raise click.Abort() from e


@cli.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for reports",
)
def generate_all_reports(output: Path | None) -> None:
    """Generate reports for all companies."""
    from .data.loaders import CompetitorDataLoader

    click.echo("📊 Generating reports for all companies...")

    try:
        loader = CompetitorDataLoader()
        companies = loader.load_companies()

        scorer = GrowthScorer()
        scored_companies = []
        for company in companies:
            scored = scorer.calculate_scores(company)
            scored_companies.append(scored)

        output_dir = output or Path("data/output/reports/all_companies")
        generator = ClientReportGenerator(output_dir=output_dir)

        generated = generator.generate_all_reports(scored_companies)

        click.echo(f"✅ Generated reports for {len(generated)} companies")
        click.echo(f"   Output directory: {output_dir}")

    except Exception as e:
        click.echo(f"❌ Failed to generate reports: {e}", err=True)
        raise click.Abort() from e


@cli.command()
def version() -> None:
    """Show version information."""
    from . import __version__

    click.echo(f"SolStein v{__version__}")
    click.echo("AI-Powered Competitive Intelligence Platform")


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
