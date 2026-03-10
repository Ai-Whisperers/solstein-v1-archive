#!/usr/bin/env python3
"""
INGEST SCRIPT: Process discovered European energy companies into Solstein pipeline.

This script:
1. Consumes JSON from research agent (50 companies with all public data)
2. Validates and normalizes data
3. Exports to compatible Solstein format
4. Runs ENEVE pipeline (scoring + export)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_company_data(company: dict) -> bool:
    """Validate that company has minimum required fields."""
    required = ["company_name", "country"]
    optional_critical = ["revenue_eur_millions", "employees"]

    # Must have company name and country
    if not all(company.get(f) for f in required):
        return False

    # Must have at least revenue OR employees (STORY-206 requirement)
    if not any(company.get(f) for f in optional_critical):
        logger.warning(f"Skipping {company.get('company_name')}: Missing revenue and employees")
        return False

    return True


def normalize_company(company: dict, index: int) -> dict:
    """Convert research data to Solstein format."""
    return {
        "company_name": company.get("company_name", f"Company-{index}"),
        "name": company.get("company_name"),
        "website": company.get("website"),
        "country": company.get("country"),
        "headquarters": company.get("country"),
        "industry": "Energy Software",
        "description": company.get("description"),
        "founded_year": company.get("founded_year"),
        "revenue": company.get("revenue_eur_millions"),
        "employees": company.get("employees"),
        "growth_rate": company.get("growth_rate_percent") / 100.0 if company.get("growth_rate_percent") else None,
        "profit_margin": company.get("profit_margin_percent") / 100.0 if company.get("profit_margin_percent") else None,
        "funding_raised": company.get("funding_raised_eur_millions"),
        "data_sources": company.get("data_sources", []),
        "confidence": company.get("confidence_score", 0.5),
        "data_quality": {
            "confidence_score": company.get("confidence_score", 0.5),
            "completeness_score": company.get("completeness_score", 0.5),
            "validation_issues": [],
            "data_sources": company.get("data_sources", []),
            "collection_method": "research_agent",
            "is_synthetic": False,
            "last_validated": datetime.now(timezone.utc).isoformat(),
        },
        "is_synthetic": False,
        "ticker": None,
        "company_number": None,
        "isin": None,
    }


def ingest_research_output(research_json_path: Path) -> dict:
    """Load and process research agent output."""
    logger.info(f"Loading research data from {research_json_path}")

    if not research_json_path.exists():
        logger.error(f"Research file not found: {research_json_path}")
        sys.exit(1)

    with open(research_json_path) as f:
        research_data = json.load(f)

    logger.info(f"Processing {len(research_data.get('companies', []))} companies...")

    # Validate and normalize
    valid_companies = []
    for index, company in enumerate(research_data.get("companies", [])):
        if validate_company_data(company):
            normalized = normalize_company(company, index)
            valid_companies.append(normalized)
        else:
            logger.warning(f"Rejected company {index}: {company.get('company_name', 'Unknown')}")

    logger.info(f"✅ Validated {len(valid_companies)}/{len(research_data.get('companies', []))} companies")

    return {
        "competitors": valid_companies,
        "metadata": {
            "source": "research_agent",
            "discovered_at": research_data.get("discovered_at"),
            "total_companies": len(valid_companies),
            "data_quality_notes": research_data.get("data_quality_notes"),
        },
    }


def export_ingested_data(data: dict, output_path: Path) -> None:
    """Export ingested data to Solstein format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"✅ Exported {len(data['competitors'])} companies to {output_path}")


def main():
    """Main ingest workflow."""
    # Paths
    research_output = Path("data/input/research_european_energy_50.json")
    solstein_input = Path("data/input/competitor_data_european_50_real.json")

    # Ingest
    ingested = ingest_research_output(research_output)

    # Export
    export_ingested_data(ingested, solstein_input)

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info(f"INGEST COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Companies processed: {len(ingested['competitors'])}")
    logger.info(f"Output location: {solstein_input}")
    logger.info(f"\nNext step: Run ENEVE pipeline")
    logger.info(f"  PYTHONPATH=src python3 scripts/run_eneve_199.py --warn-mode")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
