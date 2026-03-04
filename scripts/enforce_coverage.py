#!/usr/bin/env python3
"""Enforce branch-specific coverage thresholds."""

import json
import os
import sys
from xml.etree import ElementTree as ET


def get_branch_type():
    """Determine branch type from git or CI environment."""
    if github_ref := os.environ.get("GITHUB_REF"):
        if github_ref.startswith("refs/heads/"):
            branch = github_ref.replace("refs/heads/", "")
        else:
            branch = github_ref
    else:
        import subprocess

        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()

    if branch in ["main", "master"]:
        return "main"
    elif branch.startswith("release"):
        return "release"
    elif branch == "develop":
        return "develop"
    elif branch.startswith("hotfix/"):
        return "hotfix"
    else:
        return "feature"


def parse_coverage_xml(xml_file="coverage.xml"):
    """Parse coverage.xml and extract line coverage percentage."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        line_rate = float(root.get("line-rate", 0)) * 100
        return line_rate
    except FileNotFoundError:
        print(f"Error: Coverage file not found: {xml_file}")
        return None


def load_thresholds(config_file="config/coverage-thresholds.json"):
    """Load coverage thresholds from config."""
    with open(config_file) as f:
        return json.load(f)


def main():
    branch_type = get_branch_type()
    config = load_thresholds()
    threshold = config["thresholds"].get(branch_type, config["thresholds"]["feature"])
    required_coverage = threshold["line_coverage"]

    actual_coverage = parse_coverage_xml()
    if actual_coverage is None:
        return 1

    print("\nCoverage Enforcement")
    print(f"   Branch Type: {branch_type}")
    print(f"   Required:    {required_coverage}%")
    print(f"   Actual:      {actual_coverage:.2f}%")
    print("   Status:      ", end="")

    if actual_coverage >= required_coverage:
        print("PASS\n")
        return 0
    else:
        shortfall = required_coverage - actual_coverage
        print(f"FAIL (needs {shortfall:.2f}% more)\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
