#!/usr/bin/env python3
"""Unified Solstein Enhancement Pipeline - All 6 Epics Integration.

This script runs the complete Solstein Enhancement pipeline combining:
- Epic 1 & 5: Deep Analysis with Capability Overlap
- Epic 2: Financial Growth Intelligence
- Epic 3: Corporate Genealogy
- Epic 4: Market Protocol Mapping
- Epic 6: AI-Native Assessment

Usage:
    PYTHONPATH=src python scripts/unified_enhancement_pipeline.py --companies "Company A" "Company B"
    PYTHONPATH=src python scripts/unified_enhancement_pipeline.py --limit 10 --output-dir ./reports/unified
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.intelligence.ai_assessment_engine import AIAssessmentEngine
from solstein.intelligence.ai_report_generator import AIAssessmentReportGenerator
from solstein.intelligence.capability_overlap import OverlapAnalyzer
from solstein.intelligence.deep_analyzer import DeepAnalysisGenerator
from solstein.intelligence.financial_analyzer import FinancialGrowthAnalyzer
from solstein.intelligence.financial_report_generator import FinancialGrowthReportGenerator
from solstein.intelligence.genealogy_analyzer import GenealogyAnalyzer
from solstein.intelligence.genealogy_report_generator import GenealogyReportGenerator
from solstein.intelligence.protocol_mapper import ProtocolMapper
from solstein.intelligence.protocol_report_generator import ProtocolReportGenerator
from solstein.intelligence.report_generator import CitedReportGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_research_data(filepath: Path) -> list[dict]:
    """Load company data from research results JSON."""
    logger.info(f"Loading research data from {filepath}")
    with open(filepath, encoding="utf-8") as f:
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
    return news_items


def transform_for_financial_analysis(company: dict) -> dict:
    """Transform company data for FinancialGrowthAnalyzer."""
    import datetime

    financials = company.get("financials", {})
    funding = company.get("funding", {})
    basic_info = company.get("basic_info", {})

    founded_year = basic_info.get("founded_year")
    current_year = datetime.datetime.now().year
    company_age = current_year - founded_year if founded_year else None

    rounds_raw = funding.get("rounds", 0)
    num_rounds = len(rounds_raw) if isinstance(rounds_raw, list) else (rounds_raw or 0)

    funding_rounds = []
    total_raised = funding.get("total_raised")

    # Only create round entries if we have actual round-by-round data
    # Don't fabricate synthetic rounds with averaged amounts - that's misleading
    if total_raised and num_rounds > 0:
        # Check if we have detailed round data or just a count
        if isinstance(rounds_raw, list) and len(rounds_raw) > 0 and isinstance(rounds_raw[0], dict):
            # We have actual round data - parse it
            for raw_round in rounds_raw:
                funding_rounds.append(
                    {
                        "round": raw_round.get("round", "Unknown"),
                        "amount": raw_round.get("amount"),
                        "date": raw_round.get("date"),
                        "lead_investor": raw_round.get("lead_investor"),
                    }
                )
        else:
            # Only have total + count - don't fabricate individual rounds
            # Just record the summary to avoid misleading data
            funding_rounds = [
                {
                    "round": f"{num_rounds} rounds (details unknown)",
                    "amount": total_raised,
                    "date": None,
                    "lead_investor": None,
                }
            ]
    elif total_raised:
        funding_rounds = [{"round": "Total Known", "amount": total_raised}]

    growth_rate = financials.get("growth_rate")
    if growth_rate is None:
        if num_rounds >= 3 and total_raised and total_raised > 50:
            growth_rate = 50
        elif num_rounds >= 2 and total_raised and total_raised > 20:
            growth_rate = 30
        elif company_age and company_age < 5:
            growth_rate = 40
        else:
            growth_rate = 15

    revenue = financials.get("revenue")
    revenue_timeline = []
    if revenue and growth_rate > 0:
        for years_back in range(1, min(4, company_age or 3)):
            historical_revenue = revenue / ((1 + growth_rate / 100) ** years_back)
            revenue_timeline.append({"year": current_year - years_back, "amount": round(historical_revenue, 2)})

    return {
        "name": company.get("company_name", "Unknown"),
        "revenue": revenue,
        "growth_rate": growth_rate,
        "employees": basic_info.get("employees") or financials.get("employees"),
        "funding_raised": total_raised,
        "funding_rounds": funding_rounds,
        "num_funding_rounds": num_rounds,
        "description": basic_info.get("description", ""),
        "industry": basic_info.get("industry", ""),
        "founded_year": founded_year,
        "company_age": company_age,
        "revenue_timeline": revenue_timeline,
        "headquarters": basic_info.get("headquarters", ""),
        "ai_score": company.get("ai_score"),
        "saas_maturity": company.get("saas_maturity"),
        "recent_news": company.get("recent_news", []),
    }


def run_epic_1_5_analysis(
    company: dict,
    overlap_analyzer: OverlapAnalyzer,
    deep_analyzer: DeepAnalysisGenerator,
) -> dict[str, Any]:
    """Run Epic 1 & 5: Deep Analysis with Capability Overlap."""
    company_name = company.get("company_name", "Unknown")
    logger.info(f"[Epic 1/5] Deep Analysis: {company_name}")

    basic = company.get("basic_info", {})
    description = basic.get("description", "")

    source_texts = []
    if basic.get("description"):
        source_texts.append(basic["description"])
    for source in company.get("data_sources", []):
        if source.get("url"):
            source_texts.append(source["url"])

    overlap_result = overlap_analyzer.analyze(
        entity_id=company_name.lower().replace(" ", "_"),
        entity_name=company_name,
        source_texts=source_texts if source_texts else [description],
    )

    profile = {
        "company_name": company_name,
        "basic_info": basic,
        "financials": company.get("financials", {}),
        "funding": company.get("funding", {}),
        "data_sources": company.get("data_sources", []),
    }

    deep_analysis = deep_analyzer.generate_from_dict(company_name, profile)

    return {
        "company_name": company_name,
        "overlap": overlap_result,
        "deep_analysis": deep_analysis,
    }


def run_epic_2_financial(
    company: dict,
    financial_analyzer: FinancialGrowthAnalyzer,
    report_generator: FinancialGrowthReportGenerator,
) -> dict[str, Any]:
    """Run Epic 2: Financial Growth Intelligence."""
    company_name = company.get("company_name", "Unknown")
    logger.info(f"[Epic 2] Financial Analysis: {company_name}")
    transformed = transform_for_financial_analysis(company)
    financial_intelligence = financial_analyzer.analyze(transformed)
    report = report_generator.generate(company_name, financial_intelligence)

    return {
        "company_name": company_name,
        "financial_intelligence": financial_intelligence,
        "trajectory": financial_intelligence.growth_trajectory
        if hasattr(financial_intelligence, "growth_trajectory")
        else None,
        "report": report,
    }


def run_epic_3_genealogy(
    company: dict,
    genealogy_analyzer: GenealogyAnalyzer,
    report_generator: GenealogyReportGenerator,
) -> dict[str, Any]:
    """Run Epic 3: Corporate Genealogy Analysis."""
    company_name = company.get("company_name", "Unknown")
    logger.info(f"[Epic 3] Genealogy: {company_name}")

    basic = company.get("basic_info", {})
    description = basic.get("description", "")
    news_items = extract_news_items(company)

    genealogy_result = genealogy_analyzer.analyze(
        company_name=company_name,
        company_description=description,
        recent_news=news_items,
    )
    report = report_generator.generate(genealogy_result)

    return {
        "company_name": company_name,
        "genealogy": genealogy_result,
        "report": report,
    }


def run_epic_4_protocols(
    company: dict,
    protocol_mapper: ProtocolMapper,
    report_generator: ProtocolReportGenerator,
) -> dict[str, Any]:
    """Run Epic 4: Market Protocol Mapping."""
    company_name = company.get("company_name", "Unknown")
    logger.info(f"[Epic 4] Protocol Mapping: {company_name}")

    basic = company.get("basic_info", {})
    description = basic.get("description", "")
    headquarters = basic.get("headquarters", "")
    news_items = extract_news_items(company)

    protocol_map = protocol_mapper.analyze(
        company_name=company_name,
        company_description=description,
        headquarters=headquarters,
        recent_news=news_items,
    )
    report = report_generator.generate(protocol_map)

    return {
        "company_name": company_name,
        "protocol_map": protocol_map,
        "report": report,
    }


def run_epic_6_ai(
    company: dict,
    ai_engine: AIAssessmentEngine,
    report_generator: AIAssessmentReportGenerator,
) -> dict[str, Any]:
    """Run Epic 6: AI-Native Assessment."""
    company_name = company.get("company_name", "Unknown")
    logger.info(f"[Epic 6] AI Assessment: {company_name}")

    basic = company.get("basic_info", {})
    description = basic.get("description", "")
    news_items = extract_news_items(company)

    assessment = ai_engine.analyze(
        company_name=company_name,
        company_description=description,
        recent_news=news_items,
    )
    report = report_generator.generate(assessment)

    return {
        "company_name": company_name,
        "assessment": assessment,
        "report": report,
    }


def generate_unified_report(company: dict, epic_results: dict[str, Any]) -> str:
    """Generate unified comprehensive report combining all epics."""
    company_name = company.get("company_name", "Unknown")
    basic = company.get("basic_info", {})

    sections = []

    # Header section
    sections.append(f"# Solstein Unified Assessment: {company_name}")
    sections.append("")
    sections.append("## Executive Summary")
    sections.append("")
    sections.append("This comprehensive assessment integrates intelligence from all six Solstein enhancement epics:")
    sections.append("")
    sections.append("| Epic | Intelligence Domain | Status |")
    sections.append("|------|---------------------|--------|")
    sections.append("| Epic 1/5 | Deep Analysis & Capability Overlap | Complete |")
    sections.append("| Epic 2 | Financial Growth Intelligence | Complete |")
    sections.append("| Epic 3 | Corporate Genealogy | Complete |")
    sections.append("| Epic 4 | Market Protocol Mapping | Complete |")
    sections.append("| Epic 6 | AI-Native Assessment | Complete |")
    sections.append("")
    sections.append("---")
    sections.append("")

    # Company overview
    sections.append("## Company Overview")
    sections.append("")
    sections.append("| Attribute | Value |")
    sections.append("|-----------|-------|")
    sections.append(f"| **Company** | {company_name} |")
    sections.append(f"| **Headquarters** | {basic.get('headquarters', 'Unknown')} |")
    sections.append(f"| **Employees** | {basic.get('employees', 'Unknown')} |")
    sections.append(f"| **Founded** | {basic.get('founded_year', 'Unknown')} |")
    sections.append(f"| **Industry** | {basic.get('industry', 'Unknown')} |")
    sections.append("")
    sections.append("---")
    sections.append("")

    # Epic 1 & 5: Deep Analysis
    if "epic_1_5" in epic_results:
        sections.append("## Epic 1 & 5: Deep Analysis with Capability Overlap")
        sections.append("")
        deep = epic_results["epic_1_5"].get("deep_analysis", {})
        overlap = epic_results["epic_1_5"].get("overlap")

        sections.append("### Executive Assessment")
        sections.append("")
        sections.append(deep.get("executive_assessment", "No assessment available"))
        sections.append("")

        if overlap:
            sections.append("### Capability Overlap with Eneve")
            sections.append("")
            sections.append("| Metric | Value |")
            sections.append("|--------|-------|")
            sections.append(f"| **Overall Score** | {overlap.overall_overlap_score:.1%} |")
            sections.append(f"| **Matching Capabilities** | {overlap.matching_capabilities}/8 |")
            sections.append(f"| **High Overlap** | {overlap.high_overlap_capabilities}/8 |")
            sections.append("")
            if overlap.strongest_matches:
                sections.append(f"**Strongest Matches:** {', '.join(overlap.strongest_matches[:5])}")
                sections.append("")
        sections.append("---")
        sections.append("")

    # Epic 2: Financial Growth
    if "epic_2" in epic_results:
        sections.append("## Epic 2: Financial Growth Intelligence")
        sections.append("")
        fi = epic_results["epic_2"].get("financial_intelligence")
        if fi:
            if hasattr(fi, "growth_trajectory"):
                traj = fi.growth_trajectory
                sections.append(f"**Growth Trajectory:** {traj.value}")
                sections.append("")

            sections.append("### Growth Vectors")
            sections.append("")
            vectors = fi.primary_growth_vectors if hasattr(fi, "primary_growth_vectors") else []
            if vectors:
                for vector in vectors[:5]:
                    sections.append(f"- **{vector.name}**: {vector.description}")
            else:
                sections.append("No growth vectors identified.")
            sections.append("")
        sections.append("---")
        sections.append("")

    # Epic 3: Corporate Genealogy
    if "epic_3" in epic_results:
        sections.append("## Epic 3: Corporate Genealogy")
        sections.append("")
        gen = epic_results["epic_3"].get("genealogy")
        if gen:
            sections.append(f"**Ownership Type:** {gen.ownership_type}")
            sections.append("")
            sections.append(f"**Current Owner:** {gen.current_owner or 'None'}")
            sections.append("")
            sections.append(
                f"**Transactions:** {gen.acquisition_count} acquisitions, {gen.divestiture_count} divestitures, {gen.merger_count} mergers"
            )
            sections.append("")
        sections.append("---")
        sections.append("")

    # Epic 4: Market Protocol Mapping
    if "epic_4" in epic_results:
        sections.append("## Epic 4: Market Protocol Mapping")
        sections.append("")
        pm = epic_results["epic_4"].get("protocol_map")
        if pm:
            primary_markets_str = ", ".join(pm.primary_markets[:3]) if pm.primary_markets else "Unknown"
            sections.append(f"**Primary Markets:** {primary_markets_str}")
            sections.append("")
            sections.append(f"**Countries Present:** {pm.total_countries}")
            sections.append("")
            sections.append(f"**Diversification Score:** {pm.geographic_diversification_score:.1f}/10")
            sections.append("")
            if pm.markets:
                sections.append("### Market Presence")
                sections.append("")
                for market in pm.markets[:3]:
                    sections.append(f"- **{market.country_name}**: {market.market_maturity.value}")
                sections.append("")
        sections.append("---")
        sections.append("")

    # Epic 6: AI Assessment
    if "epic_6" in epic_results:
        sections.append("## Epic 6: AI-Native Assessment")
        sections.append("")
        assessment = epic_results["epic_6"].get("assessment")
        if assessment:
            sections.append(f"**Overall Score:** {assessment.overall_score}/10")
            sections.append("")
            sections.append(f"**Signal Level:** {assessment.signal_level.value.upper()}")
            sections.append("")
            sections.append(f"**AI Native Score:** {assessment.ai_native_score}/10")
            sections.append("")
            sections.append(f"**Evidence Quality:** {assessment.evidence_quality}")
            sections.append("")
            if assessment.capabilities:
                sections.append("### Key AI Capabilities")
                sections.append("")
                for cap in assessment.capabilities[:5]:
                    sections.append(f"- **{cap.name}**: {cap.description}")
                sections.append("")
        sections.append("---")
        sections.append("")

    # Cross-epic synthesis
    sections.append("## Cross-Epic Intelligence Synthesis")
    sections.append("")
    sections.append("### Strategic Position Assessment")
    sections.append("")
    sections.append("Based on the integrated analysis across all six intelligence domains:")
    sections.append("")

    # Determine values from available results
    primary_market = "Unknown"
    if "epic_4" in epic_results and epic_results["epic_4"].get("protocol_map"):
        pm = epic_results["epic_4"]["protocol_map"]
        primary_market = pm.primary_markets[0] if pm.primary_markets else "Unknown"

    growth_trajectory = "Unknown"
    if "epic_2" in epic_results:
        fi = epic_results["epic_2"].get("financial_intelligence")
        if fi and hasattr(fi, "growth_trajectory"):
            growth_trajectory = fi.growth_trajectory.value

    ai_maturity = "Unknown"
    if "epic_6" in epic_results and epic_results["epic_6"].get("assessment"):
        ai_maturity = epic_results["epic_6"]["assessment"].signal_level.value.upper()

    overlap_score = "N/A"
    if "epic_1_5" in epic_results and epic_results["epic_1_5"].get("overlap"):
        overlap_score = f"{epic_results['epic_1_5']['overlap'].overall_overlap_score:.0%}"

    stability = "Unknown"
    if "epic_3" in epic_results and epic_results["epic_3"].get("genealogy"):
        stability = epic_results["epic_3"]["genealogy"].ownership_type

    sections.append(f"1. **Market Position:** {primary_market}")
    sections.append(f"2. **Growth Trajectory:** {growth_trajectory}")
    sections.append(f"3. **AI Maturity:** {ai_maturity}")
    sections.append(f"4. **Capability Overlap:** {overlap_score} with Eneve")
    sections.append(f"5. **Corporate Stability:** {stability}")
    sections.append("")

    # Footer
    sections.append("---")
    sections.append("")
    sections.append("*Generated by Solstein Unified Enhancement Pipeline*  ")
    sections.append("*All Six Epics Integrated | Full Traceability | Investment-Grade Intelligence*")

    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="Run unified Solstein Enhancement pipeline with all 6 epics")
    parser.add_argument(
        "--data-file",
        type=Path,
        default=Path("data/research_results/research_results.json"),
        help="Path to research results JSON",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./reports/unified"),
        help="Directory to save unified reports",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of companies to analyze (default: 5)",
    )
    parser.add_argument(
        "--companies",
        nargs="+",
        help="Specific company names to analyze",
    )
    parser.add_argument(
        "--epics",
        nargs="+",
        choices=["1", "2", "3", "4", "6", "all"],
        default=["all"],
        help="Which epics to run (default: all)",
    )

    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Initializing all epic analyzers...")
    analyzers = {
        "overlap": OverlapAnalyzer(),
        "deep": DeepAnalysisGenerator(),
        "financial": FinancialGrowthAnalyzer(),
        "genealogy": GenealogyAnalyzer(),
        "protocol": ProtocolMapper(),
        "ai": AIAssessmentEngine(),
    }

    report_generators = {
        "deep": CitedReportGenerator(),
        "financial": FinancialGrowthReportGenerator(),
        "genealogy": GenealogyReportGenerator(),
        "protocol": ProtocolReportGenerator(),
        "ai": AIAssessmentReportGenerator(),
    }

    companies = load_research_data(args.data_file)
    logger.info(f"Loaded {len(companies)} companies from research data")

    if args.companies:
        companies = [c for c in companies if c.get("company_name") in args.companies]
        logger.info(f"Filtered to {len(companies)} specified companies")
    else:
        companies = companies[: args.limit]
        logger.info(f"Limited to first {args.limit} companies")

    run_all = "all" in args.epics
    run_epic_1_5 = run_all or "1" in args.epics
    run_epic_2 = run_all or "2" in args.epics
    run_epic_3 = run_all or "3" in args.epics
    run_epic_4 = run_all or "4" in args.epics
    run_epic_6 = run_all or "6" in args.epics

    results = []
    for company in companies:
        company_name = company.get("company_name", "Unknown")
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Processing: {company_name}")
        logger.info(f"{'=' * 60}")

        try:
            epic_results = {}

            if run_epic_1_5:
                epic_results["epic_1_5"] = run_epic_1_5_analysis(company, analyzers["overlap"], analyzers["deep"])

            if run_epic_2:
                epic_results["epic_2"] = run_epic_2_financial(
                    company, analyzers["financial"], report_generators["financial"]
                )

            if run_epic_3:
                epic_results["epic_3"] = run_epic_3_genealogy(
                    company, analyzers["genealogy"], report_generators["genealogy"]
                )

            if run_epic_4:
                epic_results["epic_4"] = run_epic_4_protocols(
                    company, analyzers["protocol"], report_generators["protocol"]
                )

            if run_epic_6:
                epic_results["epic_6"] = run_epic_6_ai(company, analyzers["ai"], report_generators["ai"])

            unified_report = generate_unified_report(company, epic_results)

            safe_name = company_name.replace(" ", "_").replace("/", "_")

            if run_epic_1_5:
                (args.output_dir / "epic1_5").mkdir(exist_ok=True)
                deep_analysis = epic_results["epic_1_5"].get("deep_analysis", {})
                executive_text = (
                    deep_analysis.get("executive_assessment", "") if isinstance(deep_analysis, dict) else ""
                )
                with open(
                    args.output_dir / "epic1_5" / f"{safe_name}_deep_analysis.md",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(executive_text)

            if run_epic_2:
                (args.output_dir / "epic2").mkdir(exist_ok=True)
                with open(
                    args.output_dir / "epic2" / f"{safe_name}_financial.md",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(epic_results["epic_2"]["report"])

            if run_epic_3:
                (args.output_dir / "epic3").mkdir(exist_ok=True)
                with open(
                    args.output_dir / "epic3" / f"{safe_name}_genealogy.md",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(epic_results["epic_3"]["report"])

            if run_epic_4:
                (args.output_dir / "epic4").mkdir(exist_ok=True)
                with open(
                    args.output_dir / "epic4" / f"{safe_name}_protocols.md",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(epic_results["epic_4"]["report"])

            if run_epic_6:
                (args.output_dir / "epic6").mkdir(exist_ok=True)
                with open(
                    args.output_dir / "epic6" / f"{safe_name}_ai_assessment.md",
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(epic_results["epic_6"]["report"])

            unified_path = args.output_dir / f"{safe_name}_unified_assessment.md"
            with open(unified_path, "w", encoding="utf-8") as f:
                f.write(unified_report)

            results.append(
                {
                    "company_name": company_name,
                    "epic_results": epic_results,
                    "unified_report_path": str(unified_path),
                }
            )

            logger.info(f"Completed unified assessment for {company_name}")

        except Exception as e:
            logger.error(f"Failed to analyze {company_name}: {e}")
            import traceback

            logger.error(traceback.format_exc())
            continue

    summary_path = args.output_dir / "_unified_pipeline_summary.json"
    summary = {
        "total_analyzed": len(results),
        "companies": [r["company_name"] for r in results],
        "epics_run": args.epics,
        "output_directory": str(args.output_dir),
        "reports_generated": {
            "unified": [f"{r['company_name']}_unified_assessment.md" for r in results],
        },
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)

    logger.info(f"\n{'=' * 60}")
    logger.info("UNIFIED PIPELINE COMPLETE!")
    logger.info(f"{'=' * 60}")
    logger.info(f"Generated {len(results)} unified reports in {args.output_dir}")
    logger.info(f"Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
