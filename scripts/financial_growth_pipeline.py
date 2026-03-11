#!/usr/bin/env python3
"""Financial growth intelligence pipeline for Epic 2."""

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.intelligence.financial_analyzer import FinancialGrowthAnalyzer
from solstein.intelligence.financial_report_generator import BatchFinancialReportGenerator


def load_companies_from_json(file_path: Path) -> list[dict]:
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "companies" in data:
        return data["companies"]
    return data if isinstance(data, list) else []


def transform_research_data(company_data: dict) -> dict:
    financials = company_data.get("financials", {})
    funding = company_data.get("funding", {})
    basic_info = company_data.get("basic_info", {})

    founded_year = basic_info.get("founded_year")
    current_year = datetime.datetime.now().year
    company_age = current_year - founded_year if founded_year else None

    rounds_raw = funding.get("rounds", 0)
    num_rounds = len(rounds_raw) if isinstance(rounds_raw, list) else (rounds_raw or 0)

    funding_rounds = []
    total_raised = funding.get("total_raised")

    if total_raised and num_rounds > 0:
        avg_per_round = total_raised / num_rounds
        for i in range(num_rounds):
            year = founded_year + (i * (company_age // max(num_rounds, 1))) if founded_year and company_age else None
            funding_rounds.append({"round": f"Round {i + 1}", "amount": round(avg_per_round, 2), "year": year})
    elif total_raised:
        funding_rounds = [{"round": "Total Known", "amount": total_raised}]

    growth_rate = financials.get("growth_rate")
    if growth_rate is None:
        growth_rate = _infer_growth_rate(num_rounds, total_raised, company_age)

    revenue = financials.get("revenue")
    revenue_timeline = _build_revenue_timeline(revenue, growth_rate, current_year, company_age)

    return {
        "name": company_data.get("company_name", "Unknown"),
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
        "ai_score": company_data.get("ai_score"),
        "saas_maturity": company_data.get("saas_maturity"),
        "recent_news": company_data.get("recent_news", []),
    }


def _infer_growth_rate(num_rounds: int, total_raised: float | None, company_age: int | None) -> int:
    if num_rounds >= 3 and total_raised and total_raised > 50:
        return 50
    if num_rounds >= 2 and total_raised and total_raised > 20:
        return 30
    if company_age and company_age < 5:
        return 40
    return 15


def _build_revenue_timeline(
    revenue: float | None, growth_rate: int, current_year: int, company_age: int | None
) -> list[dict]:
    if not revenue:
        return []

    timeline = [{"year": current_year, "amount": revenue}]

    if growth_rate > 0:
        for years_back in range(1, min(4, company_age or 3)):
            historical_revenue = revenue / ((1 + growth_rate / 100) ** years_back)
            timeline.append({"year": current_year - years_back, "amount": round(historical_revenue, 2)})

    return timeline


def run_pipeline(input_file: Path, output_dir: Path, limit: int | None = None) -> list[Path]:
    print(f"Loading company data from {input_file}")
    companies = load_companies_from_json(input_file)
    print(f"Loaded {len(companies)} companies")

    if limit:
        companies = companies[:limit]
        print(f"Processing first {limit} companies")

    analyzer = FinancialGrowthAnalyzer()
    batch_generator = BatchFinancialReportGenerator()

    results = []
    for i, company_data in enumerate(companies, 1):
        name = company_data.get("company_name", f"Company_{i}")
        print(f"\n[{i}/{len(companies)}] Analyzing {name}...")

        try:
            transformed = transform_research_data(company_data)
            financial_intelligence = analyzer.analyze(transformed)
            results.append((name, financial_intelligence))

            print(f"  Revenue: €{transformed.get('revenue', 'N/A')}M")
            print(f"  Growth: {transformed.get('growth_rate', 'N/A')}%")
            print(f"  Trajectory: {financial_intelligence.growth_trajectory.value}")
            print(f"  Vectors: {len(financial_intelligence.primary_growth_vectors)}")
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    print(f"\nGenerating reports in {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_paths = batch_generator.generate_batch(results, output_dir)
    print(f"Generated {len(report_paths)} reports")

    summary = batch_generator.generate_summary_table(results)
    summary_path = output_dir / "financial_growth_summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"Summary saved to {summary_path}")

    json_results = {name: fi.to_dict() for name, fi in results}
    json_path = output_dir / "financial_intelligence_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_results, f, indent=2, default=str)
    print(f"JSON results saved to {json_path}")

    return report_paths


def main():
    parser = argparse.ArgumentParser(description="Financial Growth Intelligence Pipeline (Epic 2)")
    parser.add_argument("--input", type=Path, default=Path("data/research_results/research_results.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/financial"))
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    report_paths = run_pipeline(input_file=args.input, output_dir=args.output_dir, limit=args.limit)
    print(f"\nPipeline complete! Generated {len(report_paths)} reports.")
    print(f"Reports saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
