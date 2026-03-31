"""Coverage truth dashboard for test coverage analysis.

G1: Build coverage truth dashboard
Provides comprehensive test coverage reporting and visualization.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger


@dataclass
class CoverageMetrics:
    """Coverage metrics for a module or file."""

    total_lines: int = 0
    covered_lines: int = 0
    missing_lines: int = 0
    coverage_percent: float = 0.0

    def __post_init__(self) -> None:
        if self.total_lines > 0:
            self.coverage_percent = (self.covered_lines / self.total_lines) * 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_lines": self.total_lines,
            "covered_lines": self.covered_lines,
            "missing_lines": self.missing_lines,
            "coverage_percent": round(self.coverage_percent, 2),
        }


@dataclass
class ModuleCoverage:
    """Coverage information for a module."""

    name: str
    path: Path
    metrics: CoverageMetrics = field(default_factory=CoverageMetrics)
    files: dict[str, CoverageMetrics] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": str(self.path),
            "metrics": self.metrics.to_dict(),
            "files": {name: m.to_dict() for name, m in self.files.items()},
        }


@dataclass
class CoverageReport:
    """Complete coverage report for the project."""

    total_metrics: CoverageMetrics = field(default_factory=CoverageMetrics)
    modules: list[ModuleCoverage] = field(default_factory=list)
    timestamp: str = ""
    threshold: float = 80.0

    @property
    def passed_threshold(self) -> bool:
        """Check if coverage meets threshold."""
        return self.total_metrics.coverage_percent >= self.threshold

    def get_low_coverage_modules(self, min_coverage: float = 60.0) -> list[ModuleCoverage]:
        """Get modules with coverage below minimum."""
        return [m for m in self.modules if m.metrics.coverage_percent < min_coverage]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "threshold": self.threshold,
            "passed_threshold": self.passed_threshold,
            "total_metrics": self.total_metrics.to_dict(),
            "modules": [m.to_dict() for m in self.modules],
            "low_coverage_modules": [m.name for m in self.get_low_coverage_modules()],
        }


class CoverageCollector:
    """Collects coverage data from pytest-cov."""

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()

    def run_coverage(self) -> dict[str, Any]:
        """Run pytest with coverage and return JSON report."""
        try:
            subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "--cov=src/solstein",
                    "--cov-report=json:/tmp/coverage.json",
                    "--cov-report=term-missing",
                    "-q",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            # Read the JSON report
            coverage_file = Path("/tmp/coverage.json")
            if coverage_file.exists():
                with open(coverage_file) as f:
                    return json.load(f)
            else:
                logger.error("Coverage JSON file not generated")
                return {}

        except Exception as e:
            logger.error("Failed to run coverage", error=str(e))
            return {}

    def parse_coverage(self, coverage_data: dict[str, Any]) -> CoverageReport:
        """Parse coverage JSON into CoverageReport."""
        report = CoverageReport()

        if not coverage_data:
            return report

        # Parse totals
        totals = coverage_data.get("totals", {})
        report.total_metrics = CoverageMetrics(
            total_lines=totals.get("num_statements", 0),
            covered_lines=totals.get("covered_lines", 0),
            missing_lines=totals.get("missing_lines", 0),
        )

        # Parse per-file coverage
        files = coverage_data.get("files", {})
        modules: dict[str, ModuleCoverage] = {}

        for file_path, file_data in files.items():
            # Skip test files
            if "test" in file_path.lower():
                continue

            # Determine module
            path_parts = Path(file_path).parts
            if "src" in path_parts:
                src_idx = path_parts.index("src")
                if len(path_parts) > src_idx + 2:
                    module_name = path_parts[src_idx + 2]  # e.g., 'analytics'
                else:
                    module_name = "root"
            else:
                module_name = "other"

            if module_name not in modules:
                modules[module_name] = ModuleCoverage(
                    name=module_name,
                    path=self.project_root / "src" / "solstein" / module_name,
                )

            metrics = CoverageMetrics(
                total_lines=file_data.get("num_statements", 0),
                covered_lines=file_data.get("executed_lines", 0),
                missing_lines=file_data.get("missing_lines", 0),
            )

            modules[module_name].files[file_path] = metrics

        # Aggregate module metrics
        for module in modules.values():
            total = sum(f.total_lines for f in module.files.values())
            covered = sum(f.covered_lines for f in module.files.values())
            module.metrics = CoverageMetrics(
                total_lines=total,
                covered_lines=covered,
            )

        report.modules = list(modules.values())
        report.modules.sort(key=lambda m: m.metrics.coverage_percent)

        return report


class CoverageDashboard:
    """Coverage dashboard for visualization and reporting.

    G1: Provides comprehensive coverage reporting.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self.project_root = project_root or Path.cwd()
        self.collector = CoverageCollector(project_root)

    def generate_report(self) -> CoverageReport:
        """Generate complete coverage report."""
        coverage_data = self.collector.run_coverage()
        report = self.collector.parse_coverage(coverage_data)
        from datetime import datetime

        report.timestamp = datetime.now().isoformat()
        return report

    def print_summary(self, report: CoverageReport | None = None) -> None:
        """Print coverage summary to console."""
        if report is None:
            report = self.generate_report()

        print("\n" + "=" * 70)
        print("COVERAGE TRUTH DASHBOARD")
        print("=" * 70)
        print(f"Timestamp: {report.timestamp}")
        print(f"Threshold: {report.threshold}%")
        print(f"Status: {'✓ PASS' if report.passed_threshold else '✗ FAIL'}")
        print("-" * 70)

        # Overall metrics
        m = report.total_metrics
        print(f"\nOverall Coverage: {m.coverage_percent:.1f}%")
        print(f"  Total Lines: {m.total_lines}")
        print(f"  Covered Lines: {m.covered_lines}")
        print(f"  Missing Lines: {m.missing_lines}")

        # Module breakdown
        print("\n" + "-" * 70)
        print("Module Coverage (sorted by coverage %):")
        print("-" * 70)

        for module in report.modules:
            status = "✓" if module.metrics.coverage_percent >= report.threshold else "⚠"
            print(
                f"{status} {module.name:20s} "
                f"{module.metrics.coverage_percent:6.1f}% "
                f"({module.metrics.covered_lines:4d}/{module.metrics.total_lines:4d} lines)"
            )

        # Low coverage modules
        low_coverage = report.get_low_coverage_modules(min_coverage=60.0)
        if low_coverage:
            print("\n" + "-" * 70)
            print("Low Coverage Modules (< 60%):")
            print("-" * 70)
            for module in low_coverage:
                print(f"  ⚠ {module.name}: {module.metrics.coverage_percent:.1f}%")

        print("\n" + "=" * 70)

    def export_html(self, report: CoverageReport, output_path: Path) -> None:
        """Export coverage report as HTML."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Coverage Truth Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #333; color: white; padding: 20px; }}
                .metric {{ display: inline-block; margin: 10px 20px; }}
                .pass {{ color: green; }}
                .fail {{ color: red; }}
                .warning {{ color: orange; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .progress-bar {{ width: 100%; background-color: #f3f3f3; }}
                .progress {{ height: 20px; background-color: #4CAF50; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Coverage Truth Dashboard</h1>
                <p>Generated: {report.timestamp}</p>
                <p class="{"pass" if report.passed_threshold else "fail"}">
                    Status: {"PASS" if report.passed_threshold else "FAIL"}
                    (Threshold: {report.threshold}%)
                </p>
            </div>

            <h2>Overall Metrics</h2>
            <div class="metric">
                <strong>Coverage:</strong> {report.total_metrics.coverage_percent:.1f}%
            </div>
            <div class="metric">
                <strong>Total Lines:</strong> {report.total_metrics.total_lines}
            </div>
            <div class="metric">
                <strong>Covered Lines:</strong> {report.total_metrics.covered_lines}
            </div>

            <h2>Module Coverage</h2>
            <table>
                <tr>
                    <th>Module</th>
                    <th>Coverage %</th>
                    <th>Lines</th>
                    <th>Status</th>
                </tr>
        """

        for module in report.modules:
            status_class = "pass" if module.metrics.coverage_percent >= report.threshold else "warning"
            status_text = "✓" if module.metrics.coverage_percent >= report.threshold else "⚠"

            html += f"""
                <tr>
                    <td>{module.name}</td>
                    <td>{module.metrics.coverage_percent:.1f}%</td>
                    <td>{module.metrics.covered_lines}/{module.metrics.total_lines}</td>
                    <td class="{status_class}">{status_text}</td>
                </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """

        output_path.write_text(html)
        logger.info("Coverage HTML report exported", path=str(output_path))


def generate_coverage_badge(coverage_percent: float, output_path: Path) -> None:
    """Generate SVG coverage badge.

    Args:
        coverage_percent: Coverage percentage
        output_path: Where to save the badge
    """
    # Determine color based on coverage
    if coverage_percent >= 80:
        color = "#4CAF50"  # Green
    elif coverage_percent >= 60:
        color = "#FFC107"  # Yellow
    else:
        color = "#F44336"  # Red

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="104" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <clipPath id="a">
        <rect width="104" height="20" rx="3" fill="#fff"/>
    </clipPath>
    <g clip-path="url(#a)">
        <path fill="#555" d="M0 0h63v20H0z"/>
        <path fill="{color}" d="M63 0h41v20H63z"/>
        <path fill="url(#b)" d="M0 0h104v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="31.5" y="15" fill="#010101" fill-opacity=".3">coverage</text>
        <text x="31.5" y="14">coverage</text>
        <text x="83.5" y="15" fill="#010101" fill-opacity=".3">{coverage_percent:.0f}%</text>
        <text x="83.5" y="14">{coverage_percent:.0f}%</text>
    </g>
</svg>
    """.strip()

    output_path.write_text(svg)


if __name__ == "__main__":
    # Run dashboard when executed directly
    dashboard = CoverageDashboard()
    report = dashboard.generate_report()
    dashboard.print_summary(report)

    # Export HTML report
    dashboard.export_html(report, Path("coverage_report.html"))

    # Generate badge
    generate_coverage_badge(report.total_metrics.coverage_percent, Path("coverage_badge.svg"))
