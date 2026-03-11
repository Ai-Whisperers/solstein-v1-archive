"""
CLI Commands for AI-Powered Research
=====================================

Autonomous company research using Ollama LLMs and web search.
Replaces synthetic data with real web-researched data.

Usage:
    solstein ai-research "Octopus Energy" --output results.json
    solstein ai-research-batch companies.txt --workers 5
    solstein ai-research-server  # Start research API server
"""

import asyncio
import json
from pathlib import Path
from typing import Any

import click
from loguru import logger

from .research.ai_research_orchestrator import AIResearchOrchestrator, ResearchReport


@click.command(name="ai-research")
@click.argument("company_name")
@click.option("--industry", "-i", help="Industry context (e.g., 'energy', 'software')")
@click.option("--max-sources", "-s", type=int, default=8, help="Maximum number of sources to research")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file for results (JSON)")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed progress")
def ai_research(company_name: str, industry: str | None, max_sources: int, output: Path | None, verbose: bool):
    """
    Perform autonomous AI-powered research on a company.

    This command uses Ollama LLMs and web search to research a company,
    extracting structured data from multiple web sources.

    Examples:
        solstein ai-research "Octopus Energy"
        solstein ai-research "Tesla" --industry automotive --max-sources 10
        solstein ai-research "Stripe" -o stripe_research.json --verbose
    """

    async def _research():
        if verbose:
            logger.info(f"🔬 Starting AI research for: {company_name}")
            if industry:
                logger.info(f"   Industry context: {industry}")
            logger.info(f"   Max sources: {max_sources}")

        orchestrator = AIResearchOrchestrator()

        try:
            report = await orchestrator.research_company(
                company_name=company_name, industry=industry, max_sources=max_sources
            )

            # Display results
            _display_report(report, verbose)

            # Save if output specified
            if output:
                output.parent.mkdir(parents=True, exist_ok=True)
                with open(output, "w") as f:
                    json.dump(_report_to_dict(report), f, indent=2)
                click.echo(f"\n💾 Results saved to: {output}")

        except Exception as e:
            logger.error(f"Research failed: {e}")
            raise click.ClickException(str(e)) from e

    asyncio.run(_research())


@click.command(name="ai-research-batch")
@click.argument("input_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default="data/research_results",
    help="Output directory for results",
)
@click.option("--workers", "-w", type=int, default=3, help="Number of concurrent research workers")
@click.option("--format", "-f", type=click.Choice(["json", "csv", "xlsx"]), default="json", help="Output format")
def ai_research_batch(input_file: Path, output_dir: Path, workers: int, format: str):
    """
    Research multiple companies from a file.

    Input file format (one company per line):
        Company Name | Industry
        Octopus Energy | Energy
        Tesla | Automotive
        Stripe | Fintech

    Examples:
        solstein ai-research-batch companies.txt --workers 5
        solstein ai-research-batch companies.txt -o results --format xlsx
    """

    async def _research_batch():
        # Parse input file
        companies = _parse_company_list(input_file)

        if not companies:
            raise click.ClickException("No companies found in input file")

        click.echo(f"🔬 Researching {len(companies)} companies with {workers} workers...")

        orchestrator = AIResearchOrchestrator()
        results = []
        errors = []

        # Process with semaphore for concurrency control
        semaphore = asyncio.Semaphore(workers)

        async def research_one(name: str, industry: str | None):
            async with semaphore:
                try:
                    report = await orchestrator.research_company(name, industry)
                    results.append(report)
                    click.echo(f"  ✅ {name}: confidence={report.confidence_score:.2f}")
                    return report
                except Exception as e:
                    errors.append({"company": name, "error": str(e)})
                    click.echo(f"  ❌ {name}: {e}")
                    return None

        # Run all research tasks
        tasks = [research_one(name, industry) for name, industry in companies]
        await asyncio.gather(*tasks)

        # Save results
        output_dir.mkdir(parents=True, exist_ok=True)

        if format == "json":
            output_file = output_dir / "research_results.json"
            data = {
                "companies": [_report_to_dict(r) for r in results],
                "errors": errors,
                "summary": {
                    "total": len(companies),
                    "successful": len(results),
                    "failed": len(errors),
                    "avg_confidence": sum(r.confidence_score for r in results) / len(results) if results else 0,
                },
            }
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)

        click.echo("\n📊 Summary:")
        click.echo(f"   Total: {len(companies)}")
        click.echo(f"   Successful: {len(results)}")
        click.echo(f"   Failed: {len(errors)}")
        if results:
            avg_conf = sum(r.confidence_score for r in results) / len(results)
            click.echo(f"   Avg Confidence: {avg_conf:.2f}")
        click.echo(f"\n💾 Results saved to: {output_dir}")

    asyncio.run(_research_batch())


@click.command(name="ai-research-server")
@click.option("--host", default="127.0.0.1", help="Server host")
@click.option("--port", type=int, default=8080, help="Server port")
@click.option("--reload", is_flag=True, help="Auto-reload on code changes")
def ai_research_server(host: str, port: int, reload: bool):
    """
    Start API server for AI research.

    Provides HTTP endpoints for:
      POST /research - Research a single company
      POST /research/batch - Research multiple companies
      GET  /research/{id} - Get research results

    Examples:
        solstein ai-research-server --port 8080

        # Then use curl:
        curl -X POST http://localhost:8080/research \\
          -H "Content-Type: application/json" \\
          -d '{"company_name": "Octopus Energy"}'
    """
    try:
        from fastapi import FastAPI
        from uvicorn import run

        app = FastAPI(title="AI Research API")
        orchestrator = AIResearchOrchestrator()

        @app.post("/research")
        async def research(request: dict[str, Any]):
            report = await orchestrator.research_company(
                company_name=request["company_name"],
                industry=request.get("industry"),
                max_sources=request.get("max_sources", 8),
            )
            return _report_to_dict(report)

        @app.post("/research/batch")
        async def research_batch(request: dict[str, Any]):
            companies = request.get("companies", [])
            results = []

            for company in companies:
                report = await orchestrator.research_company(
                    company_name=company["name"],
                    industry=company.get("industry"),
                    max_sources=company.get("max_sources", 8),
                )
                results.append(_report_to_dict(report))

            return {"results": results}

        click.echo(f"🚀 Starting AI Research API server on {host}:{port}")
        run(app, host=host, port=port, reload=reload)

    except ImportError as e:
        raise click.ClickException(
            "FastAPI and uvicorn required for server mode. Install with: pip install fastapi uvicorn"
        ) from e


# ============================================================================
# Helper Functions
# ============================================================================


def _display_report(report: ResearchReport, verbose: bool):
    """Display research report in terminal."""

    click.echo(f"\n{'=' * 60}")
    click.echo(f"📊 RESEARCH REPORT: {report.company_name}")
    click.echo(f"{'=' * 60}")

    # Confidence
    conf_color = "green" if report.confidence_score > 0.7 else "yellow" if report.confidence_score > 0.4 else "red"
    click.echo(f"\n🎯 Confidence Score: {click.style(f'{report.confidence_score:.2f}', fg=conf_color)}")
    click.echo(f"📡 Data Sources: {len(report.data_sources)}")

    # Basic Info
    click.echo("\n🏢 Basic Information:")
    basic = report.basic_info
    if basic.get("website"):
        click.echo(f"   Website: {basic['website']}")
    if basic.get("description"):
        desc = basic["description"][:100] + "..." if len(basic["description"]) > 100 else basic["description"]
        click.echo(f"   Description: {desc}")
    if basic.get("industry"):
        click.echo(f"   Industry: {basic['industry']}")
    if basic.get("headquarters"):
        click.echo(f"   Headquarters: {basic['headquarters']}")
    if basic.get("founded_year"):
        click.echo(f"   Founded: {basic['founded_year']}")
    if basic.get("employees"):
        try:
            click.echo(f"   Employees: {int(basic['employees']):,}")
        except (ValueError, TypeError):
            click.echo(f"   Employees: {basic['employees']}")

    # Financials
    if report.financials:
        click.echo("\n💰 Financials:")
        fin = report.financials
        if fin.get("revenue"):
            click.echo(f"   Revenue: €{fin['revenue']:.1f}M ({fin.get('revenue_currency', 'EUR')})")
        if fin.get("valuation"):
            click.echo(f"   Valuation: €{fin['valuation']:.1f}M")

    # Funding
    if report.funding and report.funding.get("total_raised"):
        click.echo("\n💸 Funding:")
        fund = report.funding
        click.echo(f"   Total Raised: €{fund['total_raised']:.1f}M")
        if fund.get("rounds"):
            rounds = fund["rounds"]
            if isinstance(rounds, list):
                click.echo(f"   Rounds: {len(rounds)}")
            elif isinstance(rounds, (int, float)):
                click.echo(f"   Rounds: {int(rounds)}")
            else:
                click.echo(f"   Rounds: {rounds}")

    # Data Sources
    if verbose and report.data_sources:
        click.echo("\n📚 Data Sources:")
        for source in report.data_sources[:5]:
            conf = source.get("confidence", 0)
            conf_str = f"{conf:.0%}"
            click.echo(f"   • {source['type']}: {conf_str} confidence")
            if verbose:
                url = source.get("url", "")[:60]
                click.echo(f"     {url}...")

    # Metadata
    if report.metadata:
        click.echo("\n⚙️  Research Metadata:")
        if "research_time_seconds" in report.metadata:
            click.echo(f"   Time: {report.metadata['research_time_seconds']:.1f}s")
        if "queries_executed" in report.metadata:
            click.echo(f"   Queries: {report.metadata['queries_executed']}")
        if "sources_found" in report.metadata:
            click.echo(f"   Sources Found: {report.metadata['sources_found']}")

    if report.errors:
        click.echo("\n⚠️  Errors:")
        for error in report.errors:
            click.echo(f"   • {error}")

    click.echo(f"\n{'=' * 60}")


def _report_to_dict(report: ResearchReport) -> dict[str, Any]:
    """Convert ResearchReport to dictionary."""
    return {
        "company_name": report.company_name,
        "is_synthetic": report.is_synthetic,
        "confidence_score": report.confidence_score,
        "basic_info": report.basic_info,
        "financials": report.financials,
        "funding": report.funding,
        "data_sources": report.data_sources,
        "metadata": report.metadata,
        "errors": report.errors,
    }


def _parse_company_list(file_path: Path) -> list[tuple[str, str | None]]:
    """Parse company list from file."""
    companies = []

    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Format: "Company Name | Industry" or just "Company Name"
            if "|" in line:
                parts = line.split("|", 1)
                name = parts[0].strip()
                industry = parts[1].strip() if len(parts) > 1 else None
            else:
                name = line
                industry = None

            companies.append((name, industry))

    return companies


def register_ai_research_commands(cli):
    """Register AI research commands with CLI."""
    cli.add_command(ai_research)
    cli.add_command(ai_research_batch)
    cli.add_command(ai_research_server)
