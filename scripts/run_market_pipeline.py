import argparse
import json
from pathlib import Path

from solstein.analytics.scoring import GrowthScorer
from solstein.domain.models import MarketAnalysis
from solstein.exporters.excel import ExcelExporter
from solstein.extractors.markdown_extractor import BatchExtractor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--market-name", required=True)
    parser.add_argument("--strict-provenance", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    batch = BatchExtractor()
    profiles = batch.extract_directory(input_dir)
    if not profiles:
        raise RuntimeError(f"No profiles extracted from {input_dir}")

    if args.strict_provenance:
        violations = batch.validate_profiles_provenance(profiles)
        (output_dir / "provenance_report.json").write_text(
            json.dumps(violations, indent=2),
            encoding="utf-8",
        )
        if violations:
            raise RuntimeError(f"Provenance validation failed for {len(violations)} profiles")

    extracted_path = output_dir / "extracted.json"
    batch.save_to_json(profiles, extracted_path)

    scorer = GrowthScorer()
    scored = [scorer.calculate_scores(company) for company in profiles]

    scored_path = output_dir / "scored.json"
    scored_path.write_text(
        json.dumps([company.model_dump(mode="json") for company in scored], indent=2),
        encoding="utf-8",
    )

    analysis = MarketAnalysis(market_name=args.market_name, companies=scored)
    analysis_path = output_dir / "market_analysis.json"
    analysis_path.write_text(
        json.dumps(analysis.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )

    ExcelExporter().create_dashboard(scored, output_dir / "dashboard.xlsx")


if __name__ == "__main__":
    main()
