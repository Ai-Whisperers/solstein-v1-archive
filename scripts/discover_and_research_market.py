import argparse
import json
from pathlib import Path

from solstein.research.pipeline import run_market_intelligence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-company", required=True)
    parser.add_argument("--market", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--max-companies", type=int, default=25)
    parser.add_argument("--keywords", nargs="*", default=[])
    parser.add_argument("--no-strict-provenance", action="store_true")
    parser.add_argument("--min-readiness-score", type=float)
    parser.add_argument("--max-contradictions", type=int)
    parser.add_argument("--min-total-sources", type=int)
    parser.add_argument("--db-dual-write", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_market_intelligence(
        seed_company=args.seed_company,
        market=args.market,
        output_dir=Path(args.output_dir),
        max_companies=args.max_companies,
        extra_keywords=args.keywords,
        strict_provenance=not args.no_strict_provenance,
        min_readiness_score=args.min_readiness_score,
        max_contradictions=args.max_contradictions,
        min_total_sources=args.min_total_sources,
        db_dual_write=args.db_dual_write,
    )
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "run_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
