#!/usr/bin/env python3
"""
Run ENEVE workflow with 199 companies.
Converts JSON data to Company models and generates outputs.

EPIC-058: Uses unified convert_to_domain_company() from loaders module.
No duplicate custom conversion logic.
"""

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parent.parent / "src"))

from solstein.analytics.constants import PHOENIX_SCORE_THRESHOLD, SALT_SCORE_THRESHOLD
from solstein.analytics.scoring import GrowthScorer
from solstein.data.loaders import convert_to_domain_company
from solstein.data.report_release_gate import ReportReleaseGate, build_export_metadata
from solstein.exporters.excel import ExcelExporter


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ENEVE 199-company workflow")
    parser.add_argument("--skip-gate", action="store_true", help="Skip release gate validation")
    parser.add_argument("--warn-mode", action="store_true", help="Log gate violations but do not block export")
    parser.add_argument(
        "--min-completeness",
        type=float,
        default=50.0,
        help="Minimum completeness percentage required for gate pass",
    )
    return parser.parse_args()


def _stage_load() -> tuple[list, list]:
    """Stage 1: Load raw JSON and convert to Company domain models."""
    print(f"\n{'=' * 60}")
    print(f"[STAGE 1/4 - LOAD] {datetime.now().strftime('%H:%M:%S')} Loading and converting company data...")
    print(f"{'=' * 60}")

    enriched_path = Path("data/input/competitor_data_real_enriched.json")
    input_path = enriched_path if enriched_path.exists() else Path("data/input/competitor_data_real.json")
    if not input_path.exists():
        raise FileNotFoundError(
            "Real data file not found. Run 'solstein research-companies' or "
            "'solstein replace-synthetic' to generate data/input/competitor_data_real.json"
        )
    with open(input_path) as f:
        data = json.load(f)

    companies_raw = data["competitors"]
    print(f"\n📊 Loaded {len(companies_raw)} companies from {input_path}")

    print("\n🔄 Converting to Company models (using unified converter)...")
    companies: list = []
    errors: list = []
    for i, raw in enumerate(companies_raw):
        try:
            company = convert_to_domain_company(raw, i)
            companies.append(company)
            if i < 3:
                print(
                    f"  ✓ {company.name}: revenue={company.financials.revenue}M, growth={company.financials.growth_rate}%"
                )
        except (ValueError, KeyError, TypeError) as e:
            errors.append((raw.get("company_name", "Unknown"), str(e)))
            if len(errors) <= 5:
                print(f"  ✗ Error converting {raw.get('company_name', 'Unknown')}: {e}")

    if errors:
        print(f"\n⚠️  {len(errors)} conversion errors (showing first 5)")
    print(f"\n✅ Successfully converted {len(companies)} companies")
    return companies, errors


def _stage_score(companies: list, args: argparse.Namespace) -> tuple[list, object]:
    """Stage 2: Score companies and run release gate."""
    print(f"\n{'=' * 60}")
    print(f"[STAGE 2/4 - SCORE] {datetime.now().strftime('%H:%M:%S')} Scoring {len(companies)} companies...")
    print(f"{'=' * 60}")
    print("\n🎯 Scoring companies...")
    scorer = GrowthScorer()
    scored: list = []
    score_errors: list = []

    for company in companies:
        try:
            scored.append(scorer.calculate_scores(company))
        except (ValueError, AttributeError) as e:
            score_errors.append((company.name, str(e)))

    print(f"✅ Successfully scored {len(scored)} companies")
    if score_errors:
        print(f"⚠️  {len(score_errors)} scoring errors")

    print("\n📈 Sample Results:")
    for company in scored[:5]:
        print(f"  {company.name}: composite={company.composite_score:.2f}, classification={company.classification}")

    print("\n🛡️  Running release gate checks...")
    gate = ReportReleaseGate(
        min_confidence=0.6,
        allow_synthetic=False,
        min_completeness_score=args.min_completeness,
        warn_mode=args.warn_mode,
        skip_gate=args.skip_gate,
    )
    gate_result = gate.evaluate(scored)
    if gate_result.passed:
        print("✅ Release gate passed")
    else:
        reason_codes = ", ".join(sorted({reason.code for reason in gate_result.reasons}))
        print(f"⚠️  Release gate reported issues: {reason_codes}")

    return scored, gate_result


def _stage_export(scored: list, export_metadata: dict) -> None:
    """Stage 3: Save JSON output and create Excel dashboard."""
    print(f"\n{'=' * 60}")
    print(f"[STAGE 3/4 - EXPORT] {datetime.now().strftime('%H:%M:%S')} Saving outputs and creating Excel dashboard...")
    print(f"{'=' * 60}")
    output_dir = Path("data/output/exports")
    output_dir.mkdir(parents=True, exist_ok=True)

    scored_path = output_dir / "eneve_full_199_scored.json"
    with open(scored_path, "w") as f:
        json.dump(
            {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "total_companies": len(scored),
                "companies": [c.model_dump(mode="json") for c in scored],
                "export_metadata": export_metadata,
            },
            f,
            indent=2,
        )
    print(f"\n💾 Saved scored data to {scored_path}")

    print("\n📊 Creating Excel dashboard...")
    try:
        ExcelExporter().create_dashboard(
            scored,
            output_dir / "eneve_full_199_dashboard.xlsx",
            metadata=export_metadata,
        )
        print("✅ Created Excel dashboard")
    except (OSError, RuntimeError) as e:
        print(f"✗ Error creating Excel dashboard: {e}")
        traceback.print_exc()


def _stage_summary(scored: list, pipeline_start: float) -> None:
    """Stage 4: Print pipeline summary statistics."""
    print(f"\n{'=' * 60}")
    print(
        f"[STAGE 4/4 - SUMMARY] {datetime.now().strftime('%H:%M:%S')} Pipeline completed in {time.time() - pipeline_start:.1f}s"
    )
    print(f"{'=' * 60}")
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    phoenix_count = sum(1 for c in scored if c.classification == "Phoenix")
    salt_count = sum(1 for c in scored if c.classification == "Salt")
    lead_count = sum(1 for c in scored if c.classification == "Lead")
    avg_score = sum(c.composite_score for c in scored) / len(scored) if scored else 0

    print(f"Total Companies: {len(scored)}")
    print(f"Average Composite Score: {avg_score:.2f}")
    print(f"Phoenix (≥{PHOENIX_SCORE_THRESHOLD}): {phoenix_count}")
    print(f"Salt ({SALT_SCORE_THRESHOLD}–{PHOENIX_SCORE_THRESHOLD}): {salt_count}")
    print(f"Lead (<{SALT_SCORE_THRESHOLD}): {lead_count}")
    print("=" * 60)


def main() -> None:
    """Orchestrate the four-stage ENEVE 199-company pipeline."""
    args = _parse_args()
    print("=" * 60)
    print("ENEVE 199-Company Workflow")
    print("=" * 60)
    pipeline_start = time.time()

    companies, _ = _stage_load()
    scored, gate_result = _stage_score(companies, args)
    export_metadata = build_export_metadata(scored, gate_result)
    _stage_export(scored, export_metadata)
    _stage_summary(scored, pipeline_start)


if __name__ == "__main__":
    main()
