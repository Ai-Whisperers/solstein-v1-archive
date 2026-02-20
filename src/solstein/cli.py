"""
Command-line interface for SolStein.
"""

from pathlib import Path

import click
from loguru import logger

from .analytics.scoring import GrowthScorer
from .data.models import CompanyProfile, MarketAnalysis
from .exporters.excel_exporter import ExcelExporter
from .extractors.markdown_extractor import BatchExtractor


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool):
    """SolStein - AI-Powered Competitive Intelligence Platform"""
    if verbose:
        logger.remove()
        logger.add(lambda msg: click.echo(msg, err=True), level="DEBUG")
    else:
        logger.remove()
        logger.add(lambda msg: click.echo(msg, err=True), level="INFO")


@cli.command()
@click.argument("input_dir", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output JSON file")
@click.option("--pattern", "-p", default="*.md", help="File pattern to match")
def extract(input_dir: Path, output: Path | None, pattern: str):
    """Extract data from markdown files."""
    click.echo(f"🔍 Extracting data from {input_dir}")

    extractor = BatchExtractor()
    profiles = extractor.extract_directory(input_dir, pattern)

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
@click.option("--template", "-t", type=click.Path(exists=True), help="Excel template file")
def export_excel(input_file: Path, output_file: Path, template: Path | None):
    """Export data to Excel dashboard."""
    click.echo(f"📊 Exporting to Excel: {output_file}")

    try:
        # Load profiles from JSON
        data = json.loads(input_file.read_text())
        profiles = [CompanyProfile(**item) for item in data]

        # Create exporter and generate dashboard
        exporter = ExcelExporter(template_path=template)
        exporter.create_dashboard(profiles, output_file)

        click.echo(f"✅ Dashboard created: {output_file}")
    except Exception as e:
        click.echo(f"❌ Failed to create dashboard: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file for scores")
def score(input_file: Path, output: Path | None):
    """Calculate growth and competitive scores."""
    click.echo("📈 Calculating scores...")

    try:
        # Load profiles
        data = json.loads(input_file.read_text())
        profiles = [CompanyProfile(**item) for item in data]

        # Calculate scores
        scorer = GrowthScorer()
        scored_profiles = []

        for profile in profiles:
            scored_profile = scorer.calculate_scores(profile)
            scored_profiles.append(scored_profile)

            # Show summary
            click.echo(f"  • {profile.name}:")
            click.echo(f"    Growth: {scored_profile.growth_score:.1f}/10")
            click.echo(f"    Financial Health: {scored_profile.financial_health_score:.1f}/10")
            click.echo(f"    Competitive Position: {scored_profile.competitive_position_score:.1f}/10")

        if output:
            # Save scored profiles
            data = [p.model_dump() for p in scored_profiles]
            output.write_text(json.dumps(data, indent=2, default=str))
            click.echo(f"💾 Saved scored profiles to {output}")

    except Exception as e:
        click.echo(f"❌ Failed to calculate scores: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option("--market-name", "-n", default="Competitive Landscape", help="Market name")
def analyze_market(input_file: Path, market_name: str):
    """Create market-level analysis."""
    click.echo(f"🌍 Analyzing market: {market_name}")

    try:
        # Load profiles
        data = json.loads(input_file.read_text())
        profiles = [CompanyProfile(**item) for item in data]

        # Create market analysis
        analysis = MarketAnalysis(
            market_name=market_name,
            companies=profiles
        )

        # Show analysis
        click.echo("📊 Market Analysis:")
        click.echo(f"  Companies: {analysis.company_count}")
        click.echo(f"  Average Growth: {analysis.average_growth_rate:.1f}%")
        click.echo(f"  Market Leaders: {len(analysis.market_leaders)}")

        for leader in analysis.market_leaders:
            click.echo(f"    • {leader.name} (Tier {leader.tier})")

    except Exception as e:
        click.echo(f"❌ Failed to analyze market: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("profile1", type=str)
@click.argument("profile2", type=str)
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
def compare(profile1: str, profile2: str, input_file: Path):
    """Compare two companies."""
    click.echo(f"⚖️ Comparing {profile1} vs {profile2}")

    try:
        # Load profiles
        data = json.loads(input_file.read_text())
        profiles = {p["id"]: CompanyProfile(**p) for p in data}

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
        raise click.Abort()


@cli.command()
def version():
    """Show version information."""
    from . import __version__
    click.echo(f"SolStein v{__version__}")
    click.echo("AI-Powered Competitive Intelligence Platform")


# Import json here to avoid circular imports
import json


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
