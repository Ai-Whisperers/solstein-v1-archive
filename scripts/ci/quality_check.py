#!/usr/bin/env python3
"""
Unified code quality checker v2.0.

Runs all quality checks in sequence and reports aggregated results.
Updated for EPIC-019 with new checks for EPIC-020 patterns.

Usage:
    python quality_check.py [--fail-fast] [--only-required]
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

# Check configurations
# required=True means CI will fail if this check fails
# required=False means check runs but won't block merge (informational)
CHECKS = [
    {
        "name": "Code Smells",
        "cmd": ["python3", "scripts/ci/code_smell_detector.py", "src/solstein"],
        "required": False,  # Informational - reports but doesn't block
        "description": "Detects god functions, god classes, bare excepts",
    },
    {
        "name": "Function Sizes",
        "cmd": [
            "python3",
            "scripts/ci/check_function_sizes.py",
            "--max-lines",
            "100",
            "--fail-on-violation",
            "src/solstein",
        ],
        "required": True,  # Blocks merge - EPIC-020 requirement
        "description": "Ensures no functions exceed 100 lines",
    },
    {
        "name": "Class Sizes",
        "cmd": [
            "python3",
            "scripts/ci/check_class_sizes.py",
            "--max-lines",
            "300",
            "--fail-on-violation",
            "src/solstein",
        ],
        "required": True,  # Blocks merge - EPIC-022 requirement
        "description": "Ensures no classes exceed 300 lines",
    },
    {
        "name": "File Sizes",
        "cmd": [
            "python3",
            "scripts/ci/check_file_sizes.py",
            "--max-lines",
            "500",
            "--fail-on-violation",
            "src/solstein",
        ],
        "required": True,  # Blocks merge - EPIC-021 requirement
        "description": "Ensures no files exceed 500 lines",
    },
    {
        "name": "Folder Structure",
        "cmd": ["python3", "scripts/ci/check_folder_structure.py", "--path", "src/solstein", "--fail-on-violation"],
        "required": True,
        "description": "Validates project folder structure",
    },
    {
        "name": "Import Cycles",
        "cmd": ["python3", "scripts/ci/detect_import_cycles.py", "src/solstein"],
        "required": True,  # NEW - Blocks merge
        "description": "Detects circular imports between modules",
    },
    {
        "name": "Dead Code",
        "cmd": ["python3", "scripts/ci/detect_dead_code.py", "src/solstein"],
        "required": False,  # NEW - Informational only
        "description": "Identifies potentially unused code",
    },
    {
        "name": "EPIC-020 Patterns",
        "cmd": ["python3", "scripts/ci/validate_epic020_patterns.py", "src/solstein"],
        "required": True,  # NEW - Blocks merge
        "description": "Validates EPIC-020 architectural patterns",
    },
    {
        "name": "Module Boundaries",
        "cmd": ["python3", "scripts/ci/enforce_module_boundaries.py", "src/solstein"],
        "required": False,  # NEW - Informational during transition
        "description": "Enforces architectural layer boundaries",
    },
    {
        "name": "Architecture Compliance",
        "cmd": ["python3", "scripts/ci/architecture_compliance.py", "src/solstein"],
        "required": False,  # Informational
        "description": "Checks for lazy imports and other violations",
    },
    {
        "name": "Code Duplication",
        "cmd": ["python3", "scripts/ci/duplication_detector.py", "--min-lines", "10", "src/solstein"],
        "required": False,  # Informational
        "description": "Detects duplicate code blocks",
    },
]


def run_check(check: dict) -> Tuple[bool, str]:
    """Run a single check and return (success, output)."""
    name = check["name"]
    cmd = check["cmd"]

    print(f"\n{'=' * 60}")
    print(f"Running: {name}")
    print(f"Description: {check.get('description', '')}")
    print("=" * 60)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        success = result.returncode == 0
        return success, result.stdout + result.stderr

    except subprocess.TimeoutExpired:
        print(f"❌ {name} timed out after 5 minutes")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ {name} failed with error: {e}")
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Run all code quality checks")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    parser.add_argument("--only-required", action="store_true", help="Only run required checks")
    parser.add_argument("--list", action="store_true", help="List all available checks")
    args = parser.parse_args()

    if args.list:
        print("Available quality checks:")
        print()
        for check in CHECKS:
            req = "[REQUIRED]" if check["required"] else "[optional]"
            print(f"  {req} {check['name']}")
            print(f"       {check.get('description', '')}")
            print()
        sys.exit(0)

    print("🔍 Starting code quality checks...")
    print(f"Checks to run: {len(CHECKS)}")
    print()

    results: List[Tuple[str, bool, bool]] = []  # (name, success, required)
    failed_required = []

    for check in CHECKS:
        if args.only_required and not check["required"]:
            continue

        success, _ = run_check(check)
        results.append((check["name"], success, check["required"]))

        if not success and check["required"]:
            failed_required.append(check["name"])
            if args.fail_fast:
                print(f"\n🛑 Fail-fast enabled, stopping after first required failure")
                break

    # Print summary
    print(f"\n{'=' * 60}")
    print("Summary")
    print("=" * 60)

    for name, success, required in results:
        status = "✅" if success else "❌"
        req_marker = " (required)" if required else " (optional)"
        print(f"{status} {name}{req_marker}")

    # Final result
    print(f"\n{'=' * 60}")
    if failed_required:
        print(f"❌ FAILED: {len(failed_required)} required check(s) failed")
        for name in failed_required:
            print(f"   - {name}")
        print()
        print("Please fix the issues above before merging.")
        sys.exit(1)
    else:
        print("✅ All required checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
