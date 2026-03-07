#!/usr/bin/env python3
"""PR Size and Complexity Limit Checker for EPIC-019 Story 2.

Checks:
- Max 500 lines changed per PR
- Max 20 functions per file
- Max 5 parameters per function

Usage:
    python check_pr_size.py                    # Check current PR
    python check_pr_size.py --base main        # Compare against main branch
    python check_pr_size.py --max-lines 500    # Custom line limit
    python check_pr_size.py --max-functions 20 # Custom function limit
    python check_pr_size.py --max-params 5     # Custom parameter limit
"""

from __future__ import annotations

import argparse
import ast
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class FunctionInfo:
    """Information about a function."""

    name: str
    line_start: int
    line_end: int
    params: int


@dataclass
class FileAnalysis:
    """Analysis results for a single file."""

    path: Path
    lines_changed: int = 0
    functions: list[FunctionInfo] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)

    @property
    def function_count(self) -> int:
        """Return number of functions in file."""
        return len(self.functions)

    @property
    def has_param_violations(self) -> bool:
        """Check if any function has too many parameters."""
        return any(f.params > 5 for f in self.functions)

    def get_param_violations(self) -> list[tuple[str, int]]:
        """Return functions with too many parameters."""
        return [(f.name, f.params) for f in self.functions if f.params > 5]


@dataclass
class PRAnalysis:
    """Complete PR analysis results."""

    files: list[FileAnalysis] = field(default_factory=list)
    total_lines_changed: int = 0
    violations: list[str] = field(default_factory=list)

    def add_violation(self, message: str) -> None:
        """Add a violation message."""
        self.violations.append(message)

    @property
    def has_violations(self) -> bool:
        """Check if PR has any violations."""
        return len(self.violations) > 0 or any(f.violations for f in self.files)


def get_changed_files(base_branch: str = "main") -> list[Path]:
    """Get list of Python files changed in current PR."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base_branch}...HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [Path(f.strip()) for f in result.stdout.split("\n") if f.strip().endswith(".py")]
        return files
    except subprocess.CalledProcessError:
        # Fallback: check all staged and unstaged Python files
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            files = [Path(f.strip()) for f in result.stdout.split("\n") if f.strip().endswith(".py")]
            return files
        except subprocess.CalledProcessError:
            return []


def count_lines_changed(file_path: Path, base_branch: str = "main") -> int:
    """Count lines changed in a file."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", f"{base_branch}...HEAD", "--", str(file_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        # Parse git diff --stat output
        # Example: "src/file.py | 10 +++---"
        line = result.stdout.strip()
        if "|" in line:
            parts = line.split("|")
            if len(parts) >= 2:
                # Extract insertions/deletions count
                stats = parts[1].strip()
                # Count total changes
                return sum(int(s) for s in stats.split() if s.isdigit())
        return 0
    except (subprocess.CalledProcessError, ValueError):
        return 0


def analyze_file(file_path: Path, max_params: int = 5) -> FileAnalysis:
    """Analyze a Python file for function count and parameter violations."""
    analysis = FileAnalysis(path=file_path)

    if not file_path.exists():
        analysis.violations.append(f"File not found: {file_path}")
        return analysis

    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count parameters (excluding self/cls)
                params = len(node.args.args) + len(node.args.kwonlyargs)
                if node.args.vararg:
                    params += 1
                if node.args.kwarg:
                    params += 1

                # Subtract 1 for self/cls in methods
                if params > 0 and node.args.args:
                    first_arg = node.args.args[0].arg
                    if first_arg in ("self", "cls"):
                        params -= 1

                func_info = FunctionInfo(
                    name=node.name,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    params=params,
                )
                analysis.functions.append(func_info)

            elif isinstance(node, ast.AsyncFunctionDef):
                # Same logic for async functions
                params = len(node.args.args) + len(node.args.kwonlyargs)
                if node.args.vararg:
                    params += 1
                if node.args.kwarg:
                    params += 1

                if params > 0 and node.args.args:
                    first_arg = node.args.args[0].arg
                    if first_arg in ("self", "cls"):
                        params -= 1

                func_info = FunctionInfo(
                    name=node.name,
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    params=params,
                )
                analysis.functions.append(func_info)

    except SyntaxError as e:
        analysis.violations.append(f"Syntax error in {file_path}: {e}")
    except Exception as e:
        analysis.violations.append(f"Error analyzing {file_path}: {e}")

    return analysis


def check_pr_size(
    base_branch: str = "main",
    max_lines: int = 500,
    max_functions: int = 20,
    max_params: int = 5,
) -> PRAnalysis:
    """Check PR against size and complexity limits."""
    analysis = PRAnalysis()

    # Get changed files
    changed_files = get_changed_files(base_branch)
    if not changed_files:
        print("ℹ️  No Python files changed in this PR")
        return analysis

    print(f"🔍 Analyzing {len(changed_files)} changed file(s)...")

    for file_path in changed_files:
        # Count lines changed
        lines_changed = count_lines_changed(file_path, base_branch)

        # Analyze file structure
        file_analysis = analyze_file(file_path, max_params)
        file_analysis.lines_changed = lines_changed
        analysis.total_lines_changed += lines_changed

        # Check function count limit
        if file_analysis.function_count > max_functions:
            file_analysis.violations.append(f"Too many functions: {file_analysis.function_count} (max {max_functions})")

        # Check parameter limits
        param_violations = file_analysis.get_param_violations()
        for func_name, param_count in param_violations:
            file_analysis.violations.append(f"Function '{func_name}' has {param_count} parameters (max {max_params})")

        analysis.files.append(file_analysis)

    # Check total lines changed
    if analysis.total_lines_changed > max_lines:
        analysis.add_violation(
            f"PR too large: {analysis.total_lines_changed} lines changed (max {max_lines})\n"
            f"💡 Consider splitting this PR into smaller, focused changes"
        )

    return analysis


def format_report(analysis: PRAnalysis, max_lines: int, max_functions: int, max_params: int) -> str:
    """Format analysis results as a report."""
    lines = []
    lines.append("=" * 70)
    lines.append("PR SIZE AND COMPLEXITY REPORT (EPIC-019 Story 2)")
    lines.append("=" * 70)
    lines.append("")

    # Summary
    lines.append("📊 SUMMARY")
    lines.append("-" * 40)
    lines.append(f"Files changed:     {len(analysis.files)}")
    lines.append(f"Lines changed:     {analysis.total_lines_changed} (max: {max_lines})")
    total_functions = sum(f.function_count for f in analysis.files)
    lines.append(f"Total functions:   {total_functions}")
    lines.append("")

    # Limits
    lines.append("📏 LIMITS")
    lines.append("-" * 40)
    lines.append(f"Max lines per PR:      {max_lines}")
    lines.append(f"Max functions/file:    {max_functions}")
    lines.append(f"Max parameters/func:   {max_params}")
    lines.append("")

    # Violations
    if analysis.has_violations:
        lines.append("❌ VIOLATIONS")
        lines.append("-" * 40)

        # PR-level violations
        if analysis.violations:
            for violation in analysis.violations:
                lines.append(f"🔴 {violation}")
            lines.append("")

        # File-level violations
        for file_analysis in analysis.files:
            if file_analysis.violations:
                lines.append(f"📁 {file_analysis.path}")
                for violation in file_analysis.violations:
                    lines.append(f"   ❌ {violation}")
                lines.append("")

        lines.append("=" * 70)
        lines.append("❌ FAILED: PR size/complexity checks failed")
        lines.append("=" * 70)
    else:
        lines.append("✅ All size and complexity checks passed!")
        lines.append("=" * 70)

    return "\n".join(lines)


def format_pr_comment(analysis: PRAnalysis, max_lines: int, max_functions: int, max_params: int) -> str:
    """Format analysis as a PR comment."""
    lines = []
    lines.append("## 📏 PR Size Check (EPIC-019 Story 2)")
    lines.append("")

    if analysis.has_violations:
        lines.append("❌ **This PR exceeds recommended size/complexity limits.**")
        lines.append("")

        if analysis.total_lines_changed > max_lines:
            lines.append(f"🔴 **PR Size**: {analysis.total_lines_changed} lines changed (max: {max_lines})")
            lines.append("💡 Consider splitting this PR into smaller, focused changes")
            lines.append("")

        file_violations = [f for f in analysis.files if f.violations]
        if file_violations:
            lines.append("### File Violations")
            for file_analysis in file_violations:
                lines.append(f"\n**{file_analysis.path}**")
                for violation in file_analysis.violations:
                    lines.append(f"- ❌ {violation}")
    else:
        lines.append("✅ **All size and complexity checks passed!**")
        lines.append(f"- Files changed: {len(analysis.files)}")
        lines.append(f"- Lines changed: {analysis.total_lines_changed}")
        lines.append(f"- Total functions: {sum(f.function_count for f in analysis.files)}")

    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check PR size and complexity limits (EPIC-019 Story 2)")
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch to compare against (default: main)",
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=500,
        help="Maximum lines changed per PR (default: 500)",
    )
    parser.add_argument(
        "--max-functions",
        type=int,
        default=20,
        help="Maximum functions per file (default: 20)",
    )
    parser.add_argument(
        "--max-params",
        type=int,
        default=5,
        help="Maximum parameters per function (default: 5)",
    )
    parser.add_argument(
        "--output",
        help="Output file for PR comment (optional)",
    )
    parser.add_argument(
        "--fail-on-violations",
        action="store_true",
        help="Exit with error code if violations found",
    )

    args = parser.parse_args()

    print(f"🔍 Checking PR against {args.base} branch...")
    print(f"   Max lines: {args.max_lines}")
    print(f"   Max functions/file: {args.max_functions}")
    print(f"   Max parameters/function: {args.max_params}")
    print()

    analysis = check_pr_size(
        base_branch=args.base,
        max_lines=args.max_lines,
        max_functions=args.max_functions,
        max_params=args.max_params,
    )

    report = format_report(analysis, args.max_lines, args.max_functions, args.max_params)
    print(report)

    # Write PR comment if output specified
    if args.output:
        pr_comment = format_pr_comment(analysis, args.max_lines, args.max_functions, args.max_params)
        Path(args.output).write_text(pr_comment, encoding="utf-8")
        print(f"\n📝 PR comment written to: {args.output}")

    if args.fail_on_violations and analysis.has_violations:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
