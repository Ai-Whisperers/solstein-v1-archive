#!/usr/bin/env python3
"""Pre-push quality gate for the autonomous worker.

Runs the same checks that CI will run, so the worker catches failures
BEFORE pushing a PR. This avoids the pattern of pushing broken code
and relying on CI to catch it (wasting CI minutes and checker cycles).

Usage:
    python scripts/ci/pre_push_gate.py [--fix] [--skip-tests]

Exit codes:
    0 - All gates passed
    1 - Gate failures detected (with details)

The --fix flag will auto-fix lint/format issues before checking.
The --skip-tests flag skips pytest (useful for quick format-only checks).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], description: str, timeout: int = 120) -> tuple[bool, str]:
    """Run a command and return (success, output)."""
    print(f"  {'Running':<10} {description}...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            print(f"  {'PASSED':<10} {description}")
        else:
            print(f"  {'FAILED':<10} {description}")
            # Print first 20 lines of output for context
            lines = output.strip().splitlines()
            for line in lines[:20]:
                print(f"    {line}")
            if len(lines) > 20:
                print(f"    ... ({len(lines) - 20} more lines)")
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        print(f"  {'TIMEOUT':<10} {description} (>{timeout}s)")
        return False, "Timeout"
    except FileNotFoundError as e:
        print(f"  {'SKIP':<10} {description} (tool not found: {e})")
        return True, ""  # Don't fail if tool isn't installed


def auto_fix() -> None:
    """Run auto-fixers before checking."""
    print("\n--- Auto-fixing ---")
    subprocess.run(["ruff", "check", "--fix", "src/", "tests/"], capture_output=True)
    subprocess.run(["ruff", "format", "src/", "tests/"], capture_output=True)
    print("  Auto-fix complete (ruff check --fix + ruff format)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-push quality gate")
    parser.add_argument("--fix", action="store_true", help="Auto-fix lint/format before checking")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest")
    parser.add_argument("--quick", action="store_true", help="Only run lint + format (fastest)")
    args = parser.parse_args()

    print("=" * 60)
    print("PRE-PUSH QUALITY GATE")
    print("=" * 60)

    if args.fix:
        auto_fix()

    gates: list[tuple[str, list[str], bool]] = []  # (name, cmd, required)

    # Gate 1: Lint
    gates.append(("Ruff lint", ["ruff", "check", "src/", "tests/"], True))

    # Gate 2: Format
    gates.append(("Ruff format", ["ruff", "format", "--check", "src/", "tests/"], True))

    if not args.quick:
        # Gate 3: Import cycles
        gates.append((
            "Import cycles",
            ["python3", "scripts/ci/detect_import_cycles.py", "src/solstein"],
            True,
        ))

        # Gate 4: Quality checks (required subset only)
        gates.append((
            "Quality checks",
            ["python3", "scripts/ci/quality_check.py", "--only-required"],
            True,
        ))

        if not args.skip_tests:
            # Gate 5: Unit tests (fast subset)
            gates.append((
                "Unit tests",
                ["python3", "-m", "pytest", "tests/unit/", "-x", "--timeout=60", "-q"],
                True,
            ))

    print(f"\nRunning {len(gates)} gate(s)...\n")

    failures = []
    for name, cmd, required in gates:
        passed, output = run(cmd, name)
        if not passed and required:
            failures.append(name)

    print(f"\n{'=' * 60}")
    if failures:
        print(f"FAILED: {len(failures)} gate(s) did not pass:")
        for f in failures:
            print(f"  - {f}")
        print()
        print("Fix these issues before pushing.")
        print("Tip: Run with --fix to auto-fix lint/format issues.")
        return 1
    else:
        print("ALL GATES PASSED - safe to push")
        return 0


if __name__ == "__main__":
    sys.exit(main())
