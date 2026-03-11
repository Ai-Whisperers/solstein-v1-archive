"""Market protocol mapping pipeline for Epic 4."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from solstein.intelligence.protocol_mapper import ProtocolMapper
from solstein.intelligence.protocol_report_generator import BatchProtocolReportGenerator


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

    mapper = ProtocolMapper()
    batch_generator = BatchProtocolReportGenerator()

    results = []
    for i, company_data in enumerate(companies, 1):
        name = company_data.get("company_name", f"Company_{i}")
        print(f"\n[{i}/{len(companies)}] Mapping protocols for {name}...")

        try:
            basic_info = company_data.get("basic_info", {})
            description = basic_info.get("description", "")
            headquarters = basic_info.get("headquarters", "")
            news = company_data.get("recent_news", [])

            protocol_map = mapper.analyze(
                company_name=name,
                company_description=description,
                headquarters=headquarters,
                recent_news=news if isinstance(news, list) else [],
            )
            results.append((name, protocol_map))

            print(f"  Countries: {protocol_map.total_countries}")
            print(f"  Protocols: {protocol_map.total_protocols}")
            print(f"  Diversification: {protocol_map.geographic_diversification_score}/10")
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    print(f"\nGenerating reports in {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_paths = batch_generator.generate_batch(results, output_dir)
    print(f"Generated {len(report_paths)} reports")

    json_results = {name: p.to_dict() for name, p in results}
    json_path = output_dir / "protocol_mapping_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_results, f, indent=2, default=str)
    print(f"JSON results saved to {json_path}")

    return report_paths


def main():
    parser = argparse.ArgumentParser(description="Market Protocol Mapping Pipeline (Epic 4)")
    parser.add_argument("--input", type=Path, default=Path("data/research_results/research_results.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports/protocols"))
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
