"""Corporate genealogy pipeline for Epic 3."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.intelligence.genealogy_analyzer import GenealogyAnalyzer
from solstein.intelligence.genealogy_report_generator import BatchGenealogyReportGenerator


def load_companies_from_json(file_path: Path) -> list[dict]:
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "companies" in data:
        return data["companies"]
    return data if isinstance(data, list) else []


def run_pipeline(input_file: Path, output_dir: Path, limit: int | None = None) -> list[Path]:
    print(f"Loading company data from {input_file}")
    companies = load_companies_from_json(input_file)
    print(f"Loaded {len(companies)} companies")

    if limit:
        companies = companies[:limit]
        print(f"Processing first {limit} companies")

    analyzer = GenealogyAnalyzer()
    batch_generator = BatchGenealogyReportGenerator()

    results = []
    for i, company_data in enumerate(companies, 1):
        name = company_data.get("company_name", f"Company_{i}")
        print(f"\n[{i}/{len(companies)}] Analyzing {name} genealogy...")

        try:
            basic_info = company_data.get("basic_info", {})
            description = basic_info.get("description", "")
            news = company_data.get("recent_news", [])

            genealogy = analyzer.analyze(
                company_name=name,
                company_description=description,
                recent_news=news if isinstance(news, list) else [],
            )
            results.append((name, genealogy))

            print(f"  Transactions: {len(genealogy.transactions)}")
            print(f"  Acquisitions: {genealogy.acquisition_count}")
            print(f"  Ownership: {genealogy.ownership_type}")
            if genealogy.current_owner:
                print(f"  Owner: {genealogy.current_owner}")
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    print(f"\nGenerating reports in {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_paths = batch_generator.generate_batch(results, output_dir)
    print(f"Generated {len(report_paths)} reports")

    json_results = {name: g.to_dict() for name, g in results}
    json_path = output_dir / "genealogy_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_results, f, indent=2, default=str)
    print(f"JSON results saved to {json_path}")

    return report_paths


def main():
    parser = argparse.ArgumentParser(description="Corporate Genealogy Pipeline (Epic 3)")
    parser.add_argument("--input", type=Path, default=Path("data/research_results/research_results.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/genealogy"))
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
