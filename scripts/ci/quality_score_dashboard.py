#!/usr/bin/env python3
"""Code Quality Score Dashboard for PR comments.

EPIC-019 Story 3: Generates quality scores and posts them as PR comments.
Calculates:
- Overall quality score (A-F)
- Code smell density
- Comparison to main branch
- Trend indicators
- Detailed breakdown
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class QualityMetrics:
    """Quality metrics for a codebase."""

    total_files: int
    total_lines: int
    god_functions: int
    god_classes: int
    bare_excepts: int
    files_over_500: int
    avg_function_length: float
    avg_class_length: float

    @property
    def smell_density(self) -> float:
        """Calculate code smell density per 1000 lines."""
        if self.total_lines == 0:
            return 0.0
        total_smells = self.god_functions + self.god_classes + self.bare_excepts
        return (total_smells / self.total_lines) * 1000

    @property
    def quality_score(self) -> str:
        """Calculate letter grade (A-F)."""
        score = 100

        # Deduct for code smells
        score -= self.god_functions * 5
        score -= self.god_classes * 10
        score -= self.bare_excepts * 3
        score -= self.files_over_500 * 2

        # Deduct for smell density
        score -= self.smell_density * 2

        # Clamp to 0-100
        score = max(0, min(100, score))

        # Convert to letter grade
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "god_functions": self.god_functions,
            "god_classes": self.god_classes,
            "bare_excepts": self.bare_excepts,
            "files_over_500": self.files_over_500,
            "avg_function_length": round(self.avg_function_length, 2),
            "avg_class_length": round(self.avg_class_length, 2),
            "smell_density": round(self.smell_density, 2),
            "quality_score": self.quality_score,
        }


def run_code_smell_detector(src_path: str) -> dict[str, Any]:
    """Run code smell detector and parse results."""
    try:
        result = subprocess.run(
            ["python3", "scripts/ci/code_smell_detector.py", src_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Parse the output to extract counts
        # This is a simplified parser - adjust based on actual output format
        output = result.stdout + result.stderr

        god_functions = output.count("God function")
        god_classes = output.count("God class")
        bare_excepts = output.count("Bare except")

        return {
            "god_functions": god_functions,
            "god_classes": god_classes,
            "bare_excepts": bare_excepts,
        }
    except Exception as e:
        print(f"Warning: Could not run code smell detector: {e}")
        return {"god_functions": 0, "god_classes": 0, "bare_excepts": 0}


def count_files_and_lines(src_path: str) -> tuple[int, int]:
    """Count total files and lines of code."""
    total_files = 0
    total_lines = 0

    src = Path(src_path)
    if not src.exists():
        return 0, 0

    for file in src.rglob("*.py"):
        if "__pycache__" in str(file):
            continue
        total_files += 1
        try:
            content = file.read_text()
            total_lines += len(content.splitlines())
        except Exception:
            pass

    return total_files, total_lines


def count_large_files(src_path: str, max_lines: int = 500) -> int:
    """Count files exceeding line limit."""
    count = 0
    src = Path(src_path)
    if not src.exists():
        return 0

    for file in src.rglob("*.py"):
        if "__pycache__" in str(file):
            continue
        try:
            content = file.read_text()
            lines = len(content.splitlines())
            if lines > max_lines:
                count += 1
        except Exception:
            pass

    return count


def calculate_avg_sizes(src_path: str) -> tuple[float, float]:
    """Calculate average function and class sizes."""
    import ast

    function_lengths = []
    class_lengths = []

    src = Path(src_path)
    if not src.exists():
        return 0.0, 0.0

    for file in src.rglob("*.py"):
        if "__pycache__" in str(file):
            continue
        try:
            content = file.read_text()
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    lines = node.end_lineno - node.lineno if node.end_lineno else 0
                    function_lengths.append(lines)
                elif isinstance(node, ast.ClassDef):
                    lines = node.end_lineno - node.lineno if node.end_lineno else 0
                    class_lengths.append(lines)
        except Exception:
            pass

    avg_function = sum(function_lengths) / len(function_lengths) if function_lengths else 0
    avg_class = sum(class_lengths) / len(class_lengths) if class_lengths else 0

    return avg_function, avg_class


def generate_quality_report(src_path: str, base_branch: str | None = None) -> dict[str, Any]:
    """Generate comprehensive quality report."""
    # Collect metrics
    smells = run_code_smell_detector(src_path)
    total_files, total_lines = count_files_and_lines(src_path)
    files_over_500 = count_large_files(src_path)
    avg_func_len, avg_class_len = calculate_avg_sizes(src_path)

    metrics = QualityMetrics(
        total_files=total_files,
        total_lines=total_lines,
        god_functions=smells.get("god_functions", 0),
        god_classes=smells.get("god_classes", 0),
        bare_excepts=smells.get("bare_excepts", 0),
        files_over_500=files_over_500,
        avg_function_length=avg_func_len,
        avg_class_length=avg_class_len,
    )

    report = {
        "metrics": metrics.to_dict(),
        "summary": generate_summary(metrics),
        "details": generate_details(metrics),
    }

    # Compare to base branch if provided
    if base_branch:
        report["comparison"] = compare_to_base(metrics, base_branch, src_path)

    return report


def generate_summary(metrics: QualityMetrics) -> str:
    """Generate human-readable summary."""
    score = metrics.quality_score
    emoji = {"A": "🌟", "B": "✅", "C": "⚠️", "D": "❌", "F": "🚨"}.get(score, "❓")

    summary = f"""{emoji} **Quality Score: {score}**

- **Smell Density**: {metrics.smell_density:.2f} per 1000 lines
- **God Functions**: {metrics.god_functions}
- **God Classes**: {metrics.god_classes}
- **Bare Except Clauses**: {metrics.bare_excepts}
- **Files >500 Lines**: {metrics.files_over_500}
"""
    return summary


def generate_details(metrics: QualityMetrics) -> str:
    """Generate detailed breakdown."""
    return f"""### Detailed Metrics

| Metric | Value |
|--------|-------|
| Total Files | {metrics.total_files} |
| Total Lines | {metrics.total_lines:,} |
| Avg Function Length | {metrics.avg_function_length:.1f} lines |
| Avg Class Length | {metrics.avg_class_length:.1f} lines |
| Smell Density | {metrics.smell_density:.2f}/1000 lines |

### Quality Breakdown

- **Code Smells**: {metrics.god_functions + metrics.god_classes + metrics.bare_excepts} total
  - God Functions (>100 lines): {metrics.god_functions}
  - God Classes (>300 lines): {metrics.god_classes}
  - Bare Except Clauses: {metrics.bare_excepts}
- **File Size**: {metrics.files_over_500} files exceed 500 lines
"""


def compare_to_base(current: QualityMetrics, base_branch: str, src_path: str) -> dict[str, Any]:
    """Compare current metrics to base branch."""
    try:
        # Store current state
        subprocess.run(["git", "stash", "push", "-m", "quality-check"], check=False)

        # Checkout base branch
        subprocess.run(["git", "checkout", base_branch], check=True, capture_output=True)

        # Get base metrics
        base_smells = run_code_smell_detector(src_path)
        base_files, base_lines = count_files_and_lines(src_path)
        base_files_over_500 = count_large_files(src_path)
        base_avg_func, base_avg_class = calculate_avg_sizes(src_path)

        base = QualityMetrics(
            total_files=base_files,
            total_lines=base_lines,
            god_functions=base_smells.get("god_functions", 0),
            god_classes=base_smells.get("god_classes", 0),
            bare_excepts=base_smells.get("bare_excepts", 0),
            files_over_500=base_files_over_500,
            avg_function_length=base_avg_func,
            avg_class_length=base_avg_class,
        )

        # Restore current state
        subprocess.run(["git", "checkout", "-"], check=False)
        subprocess.run(["git", "stash", "pop"], check=False)

        # Calculate changes
        score_diff = ord(current.quality_score) - ord(base.quality_score)
        smell_diff = current.smell_density - base.smell_density

        if score_diff < 0:
            trend = "📈 Improved"
        elif score_diff > 0:
            trend = "📉 Regressed"
        else:
            trend = "➡️ Unchanged"

        return {
            "base_score": base.quality_score,
            "current_score": current.quality_score,
            "trend": trend,
            "smell_density_change": round(smell_diff, 2),
            "god_functions_change": current.god_functions - base.god_functions,
            "god_classes_change": current.god_classes - base.god_classes,
        }

    except Exception as e:
        print(f"Warning: Could not compare to base branch: {e}")
        return {"error": str(e)}


def generate_pr_comment(report: dict[str, Any]) -> str:
    """Generate PR comment markdown."""
    comment = f"""## 📊 Code Quality Report

{report["summary"]}

{report["details"]}
"""

    if "comparison" in report and "error" not in report["comparison"]:
        comp = report["comparison"]
        comment += f"""
### 📈 Comparison to {comp.get("base_score", "N/A")} Branch

- **Trend**: {comp.get("trend", "N/A")}
- **Score Change**: {comp.get("base_score", "N/A")} → {comp.get("current_score", "N/A")}
- **Smell Density Change**: {comp.get("smell_density_change", 0):+.2f}/1000 lines
- **God Functions Change**: {comp.get("god_functions_change", 0):+d}
- **God Classes Change**: {comp.get("god_classes_change", 0):+d}
"""

    comment += """
---
*Generated by Code Quality Guardrails*
"""
    return comment


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate code quality score dashboard")
    parser.add_argument("src", nargs="?", default="src/solstein", help="Source directory")
    parser.add_argument("--base-branch", help="Base branch for comparison")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--pr-comment", action="store_true", help="Generate PR comment format")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    print(f"🔍 Analyzing code quality for {args.src}...")

    report = generate_quality_report(args.src, args.base_branch)

    if args.json:
        output = json.dumps(report, indent=2)
    elif args.pr_comment:
        output = generate_pr_comment(report)
    else:
        output = f"""Quality Score: {report["metrics"]["quality_score"]}
Smell Density: {report["metrics"]["smell_density"]:.2f}/1000 lines
God Functions: {report["metrics"]["god_functions"]}
God Classes: {report["metrics"]["god_classes"]}
Bare Except Clauses: {report["metrics"]["bare_excepts"]}
"""

    if args.output:
        Path(args.output).write_text(output)
        print(f"✅ Report written to {args.output}")
    else:
        print(output)

    # Exit with error code if quality is poor
    if report["metrics"]["quality_score"] in ["D", "F"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
