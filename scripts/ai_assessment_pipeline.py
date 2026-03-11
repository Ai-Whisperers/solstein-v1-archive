#!/usr/bin/env python3
"""AI Assessment Pipeline - Integration script for Epic 6.

This script runs the AI-Native Assessment pipeline:
1. Load company data from research_results.json
2. Run AI signal detection and capability analysis
3. Generate AI maturity assessments
4. Export markdown reports with methodology

Usage:
    PYTHONPATH=src python scripts/ai_assessment_pipeline.py --output-dir ./reports/ai
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.intelligence.ai_assessment_engine import AIAssessmentEngine
from solstein.intelligence.ai_report_generator import AIAssessmentExporter, AIAssessmentReportGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_research_data(filepath: Path) -> list[dict]:
    """Load company data from research results JSON."""
    logger.info(f"Loading research data from {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("companies", [])


def extract_news_items(company: dict) -> list[str]:
    """Extract news items from company data."""
    news_items = []

    data_sources = company.get("data_sources", [])
    for source in data_sources:
        if source.get("content"):
            news_items.append(source["content"])
        if source.get("title"):
            news_items.append(source["title"])

    news_data = company.get("news", {})
    if news_data.get("articles"):
        for article in news_data["articles"]:
            if isinstance(article, dict):
                if article.get("title"):
                    news_items.append(article["title"])
                if article.get("summary"):
                    news_items.append(article["summary"])
            elif isinstance(article, str):
                news_items.append(article)

    return news_items


def analyze_company(
    company: dict,
    engine: AIAssessmentEngine,
    report_gen: AIAssessmentReportGenerator,
) -> dict[str, Any]:
    """Run AI assessment on a single company."""
    company_name = company.get("company_name", "Unknown")
    logger.info(f"Analyzing AI capabilities: {company_name}")

    basic = company.get("basic_info", {})
    description = basic.get("description", "")

    if not description:
        financials = company.get("financials", {})
        description = financials.get("business_model", "")

    news_items = extract_news_items(company)

    assessment = engine.analyze(
        company_name=company_name,
        company_description=description,
        recent_news=news_items if news_items else None,
    )

    report_md = report_gen.generate(assessment)

    return {
        "company_name": company_name,
        "assessment": assessment,
        "report": report_md,
        "signal_level": assessment.signal_level.value,
        "overall_score": assessment.overall_score,
        "capabilities_count": len(assessment.capabilities),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate AI-Native Assessment reports for Solstein companies")
    parser.add_argument(
        "--data-file",
        type=Path,
        default=Path("data/research_results/research_results.json"),
        help="Path to research results JSON",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("./reports/ai"), help="Directory to save markdown reports"
    )
    parser.add_argument("--limit", type=int, default=10, help="Number of companies to analyze (default: 10)")
    parser.add_argument("--companies", nargs="+", help="Specific company names to analyze")
    parser.add_argument("--min-score", type=float, default=0.0, help="Minimum AI score to include (default: 0.0)")
    parser.add_argument(
        "--signal-filter",
        choices=["native", "adopted", "experimental", "absent", "all"],
        default="all",
        help="Filter by AI signal level (default: all)",
    )

    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Initializing AI Assessment Engine...")
    engine = AIAssessmentEngine()
    report_gen = AIAssessmentReportGenerator()
    exporter = AIAssessmentExporter()

    companies = load_research_data(args.data_file)
    logger.info(f"Loaded {len(companies)} companies from research data")

    if args.companies:
        companies = [c for c in companies if c.get("company_name") in args.companies]
        logger.info(f"Filtered to {len(companies)} specified companies")
    else:
        companies = companies[: args.limit]
        logger.info(f"Limited to first {args.limit} companies")

    results = []
    for company in companies:
        try:
            result = analyze_company(company, engine, report_gen)

            if result["overall_score"] < args.min_score:
                logger.info(f"Skipping {result['company_name']} (score {result['overall_score']} < {args.min_score})")
                continue

            if args.signal_filter != "all" and result["signal_level"] != args.signal_filter:
                logger.info(
                    f"Skipping {result['company_name']} (signal {result['signal_level']} != {args.signal_filter})"
                )
                continue

            results.append(result)

            company_name = result["company_name"]
            safe_name = company_name.replace(" ", "_").replace("/", "_")
            report_path = args.output_dir / f"{safe_name}_ai_assessment.md"

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(result["report"])

            logger.info(
                f"Saved AI assessment: {report_path} "
                f"(Signal: {result['signal_level'].upper()}, Score: {result['overall_score']}/10)"
            )

        except (ValueError, KeyError, TypeError, RuntimeError) as e:
            logger.error(f"Failed to analyze {company.get('company_name', 'Unknown')}: {e}")
            continue

    if len(results) > 1:
        comparison = exporter.generate_comparison_table([r["assessment"] for r in results])
        comparison_path = args.output_dir / "_comparison_table.md"
        with open(comparison_path, "w", encoding="utf-8") as f:
            f.write(comparison)
        logger.info(f"Saved comparison table: {comparison_path}")

    summary_path = args.output_dir / "_ai_assessment_summary.json"

    signal_distribution = {}
    for r in results:
        signal = r["signal_level"]
        signal_distribution[signal] = signal_distribution.get(signal, 0) + 1

    avg_score = sum(r["overall_score"] for r in results) / len(results) if results else 0
    avg_capabilities = sum(r["capabilities_count"] for r in results) / len(results) if results else 0

    summary = {
        "total_analyzed": len(results),
        "companies": [r["company_name"] for r in results],
        "signal_distribution": signal_distribution,
        "average_score": round(avg_score, 2),
        "average_capabilities": round(avg_capabilities, 1),
        "output_directory": str(args.output_dir),
        "reports_generated": [f"{r['company_name']}_ai_assessment.md" for r in results],
        "methodology": {
            "signal_categories": {
                "core": "Explicit AI-native positioning (3x weight)",
                "strong": "Clear AI terminology (2x weight)",
                "moderate": "Related concepts (1x weight)",
            },
            "scoring_weights": {
                "ai_native_score": "60%",
                "ai_adoption_score": "40%",
            },
            "capability_taxonomy": [
                "predictive_analytics",
                "natural_language_processing",
                "computer_vision",
                "optimization",
                "anomaly_detection",
                "forecasting",
                "automation",
                "recommendation",
            ],
        },
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    logger.info(f"AI Assessment complete! Generated {len(results)} reports in {args.output_dir}")
    logger.info(f"Summary saved to: {summary_path}")

    if results:
        logger.info(f"Signal Distribution: {signal_distribution}")
        logger.info(f"Average AI Score: {avg_score:.1f}/10")
        logger.info(f"Average Capabilities per Company: {avg_capabilities:.1f}")


if __name__ == "__main__":
    main()
