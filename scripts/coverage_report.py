#!/usr/bin/env python3
"""Test coverage tracker and reporter.

EPIC-029 Story 6: Track and enforce test coverage.

Usage:
    # Generate coverage report
    python scripts/coverage_report.py

    # Check coverage threshold
    python scripts/coverage_report.py --threshold 80

    # Report missing coverage
    python scripts/coverage_report.py --missing
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CoverageMetrics:
    """Coverage metrics for a module."""

    module: str
    statements: int
    missing: int
    coverage: float
    missing_lines: list[int] = field(default_factory=list)


@dataclass
class CoverageReport:
    """Complete coverage report."""

    total_coverage: float
    total_statements: int
    total_missing: int
    modules: list[CoverageMetrics]
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "summary": {
                "total_coverage": round(self.total_coverage, 2),
                "total_statements": self.total_statements,
                "total_missing": self.total_missing,
            },
            "modules": [
                {
                    "module": m.module,
                    "statements": m.statements,
                    "missing": m.missing,
                    "coverage": round(m.coverage, 2),
                    "missing_lines": m.missing_lines,
                }
                for m in self.modules
            ],
        }


class CoverageTracker:
    """Track test coverage."""

    def __init__(self, source_dir: str = "src/solstein"):
        """Initialize tracker.

        Args:
            source_dir: Source directory to measure.
        """
        self.source_dir = source_dir

    def run_coverage(self) -> CoverageReport | None:
        """Run coverage analysis.

        Returns:
            Coverage report or None if failed.
        """
        try:
            # Run pytest with coverage
            result = subprocess.run(
                [
                    "pytest",
                    "--cov=src/solstein",
                    "--cov-report=json",
                    "--cov-report=term-missing",
                    "-q",
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
            )

            # Parse coverage JSON
            coverage_file = Path("coverage.json")
            if coverage_file.exists():
                with open(coverage_file) as f:
                    data = json.load(f)
                coverage_file.unlink()  # Clean up
                return self._parse_coverage(data)

            return None

        except FileNotFoundError:
            print("Error: pytest or coverage not installed")
            return None
        except Exception as e:
            print(f"Coverage error: {e}")
            return None

    def _parse_coverage(self, data: dict) -> CoverageReport:
        """Parse coverage JSON data.

        Args:
            data: Coverage JSON data.

        Returns:
            Coverage report.
        """
        from datetime import datetime

        totals = data.get("totals", {})
        files = data.get("files", {})

        modules = []
        for filepath, file_data in files.items():
            summary = file_data.get("summary", {})
            modules.append(
                CoverageMetrics(
                    module=filepath,
                    statements=summary.get("num_statements", 0),
                    missing=summary.get("missing_lines", 0),
                    coverage=summary.get("percent_covered", 0.0),
                    missing_lines=file_data.get("missing_lines", []),
                )
            )

        # Sort by coverage (lowest first)
        modules.sort(key=lambda m: m.coverage)

        return CoverageReport(
            total_coverage=totals.get("percent_covered", 0.0),
            total_statements=totals.get("num_statements", 0),
            total_missing=totals.get("missing_lines", 0),
            modules=modules,
            timestamp=datetime.now().isoformat(),
        )

    def check_threshold(self, report: CoverageReport, threshold: float) -> bool:
        """Check if coverage meets threshold.

        Args:
            report: Coverage report.
            threshold: Minimum coverage percentage.

        Returns:
            True if threshold met.
        """
        return report.total_coverage >= threshold

    def get_uncovered_modules(self, report: CoverageReport, min_coverage: float = 80.0) -> list[CoverageMetrics]:
        """Get modules below coverage threshold.

        Args:
            report: Coverage report.
            min_coverage: Minimum acceptable coverage.

        Returns:
            List of under-covered modules.
        """
        return [m for m in report.modules if m.coverage < min_coverage]


def print_report(report: CoverageReport):
    """Print coverage report.

    Args:
        report: Coverage report.
    """
    print("\n" + "=" * 60)
    print("TEST COVERAGE REPORT")
    print("=" * 60)
    print(f"Timestamp: {report.timestamp}")
    print(f"\nSummary:")
    print(f"  Total Coverage: {report.total_coverage:.1f}%")
    print(f"  Statements: {report.total_statements}")
    print(f"  Missing: {report.total_missing}")

    if report.modules:
        print(f"\nModules (sorted by coverage):")
        print("-" * 60)
        print(f"{'Module':<40} {'Coverage':>10} {'Missing':>8}")
        print("-" * 60)

        for m in report.modules[:20]:  # Show top 20
            status = "✅" if m.coverage >= 80 else "⚠️" if m.coverage >= 50 else "❌"
            print(f"{status} {m.module:<38} {m.coverage:>8.1f}% {m.missing:>8}")

        if len(report.modules) > 20:
            print(f"\n... and {len(report.modules) - 20} more modules")

    print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test Coverage Tracker")
    parser.add_argument("--threshold", type=float, default=80.0, help="Coverage threshold")
    parser.add_argument("--missing", action="store_true", help="Show missing coverage")
    parser.add_argument("--output", type=str, help="Output JSON file")
    parser.add_argument("--fail-under", action="store_true", help="Exit error if under threshold")

    args = parser.parse_args()

    tracker = CoverageTracker()
    report = tracker.run_coverage()

    if not report:
        print("❌ Failed to generate coverage report")
        sys.exit(1)

    print_report(report)

    # Show missing coverage
    if args.missing:
        uncovered = tracker.get_uncovered_modules(report, args.threshold)
        if uncovered:
            print(f"\n❌ Modules below {args.threshold}% coverage:")
            for m in uncovered[:10]:
                print(f"  - {m.module}: {m.coverage:.1f}%")
                if m.missing_lines:
                    lines = ", ".join(map(str, m.missing_lines[:10]))
                    print(f"    Missing lines: {lines}")

    # Save output
    if args.output:
        with open(args.output, "w") as f:
            json.dump(report.to_dict(), f, indent=2)
        print(f"\n📄 Report saved to: {args.output}")

    # Check threshold
    passed = tracker.check_threshold(report, args.threshold)

    if args.fail_under and not passed:
        print(f"\n❌ Coverage {report.total_coverage:.1f}% is below threshold {args.threshold}%")
        sys.exit(1)

    if passed:
        print(f"\n✅ Coverage {report.total_coverage:.1f}% meets threshold {args.threshold}%")
    else:
        print(f"\n⚠️ Coverage {report.total_coverage:.1f}% is below threshold {args.threshold}%")

    sys.exit(0)


if __name__ == "__main__":
    main()
