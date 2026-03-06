#!/usr/bin/env python3
"""
Coverage enforcement script for CI/CD pipeline.
Ensures code coverage meets minimum threshold.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Minimum coverage threshold
MIN_COVERAGE = 80.0


def parse_coverage_report(coverage_file: str = "coverage.xml") -> float:
    """Parse coverage report and extract line coverage percentage."""
    if not Path(coverage_file).exists():
        print(f"Error: Coverage file '{coverage_file}' not found")
        sys.exit(1)

    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()

        # Get line coverage from the root element
        line_rate = float(root.attrib.get("line-rate", 0))
        coverage = line_rate * 100

        return coverage
    except Exception as e:
        print(f"Error parsing coverage file: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    coverage = parse_coverage_report()

    print(f"Code Coverage: {coverage:.2f}%")
    print(f"Minimum Required: {MIN_COVERAGE}%")

    if coverage < MIN_COVERAGE:
        print(f"\n❌ FAILED: Coverage {coverage:.2f}% is below minimum {MIN_COVERAGE}%")
        print(f"   Need {MIN_COVERAGE - coverage:.2f}% more coverage")
        sys.exit(1)
    else:
        print(f"\n✅ PASSED: Coverage meets minimum requirement")
        excess = coverage - MIN_COVERAGE
        if excess > 0:
            print(f"   {excess:.2f}% above minimum")
        sys.exit(0)


if __name__ == "__main__":
    main()
