#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=str(cwd))
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-file",
        default="data/input/european_energy_companies.txt",
    )
    parser.add_argument(
        "--output-dir",
        default="data/research_results",
    )
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--skip-batch",
        action="store_true",
    )
    parser.add_argument(
        "--skip-excel",
        action="store_true",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output_dir = repo_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    input_file = repo_root / args.input_file
    results_json = output_dir / "research_results.json"
    output_xlsx = output_dir / "european_energy_dashboard.xlsx"

    if not args.skip_batch:
        run(
            [
                "solstein",
                "ai-research-batch",
                str(input_file),
                "-o",
                str(output_dir),
                "-w",
                str(args.workers),
                "-f",
                "json",
            ],
            repo_root,
        )

    if not args.skip_excel:
        run(
            [
                sys.executable,
                "scripts/generate_excel_dashboard.py",
                str(results_json),
                str(output_xlsx),
            ],
            repo_root,
        )

    print(f"Pipeline complete. JSON: {results_json}")
    print(f"Pipeline complete. XLSX: {output_xlsx}")


if __name__ == "__main__":
    main()
