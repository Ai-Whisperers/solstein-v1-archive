#!/usr/bin/env python3
"""Scan files for secret patterns."""

import json
import re
import sys
from pathlib import Path


def load_patterns(config_file="config/secret-patterns.json"):
    """Load secret patterns from config."""
    with open(config_file) as f:
        return json.load(f)


def should_exclude(path, exclusions):
    """Check if file should be excluded from scanning."""
    path_str = str(path)
    return any(exclude_path in path_str for exclude_path in exclusions.get("paths", []))


def scan_file(file_path, patterns, exclusions):
    """Scan a single file for secrets."""
    if should_exclude(file_path, exclusions):
        return []

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception:
        return []

    findings = []
    for pattern_def in patterns:
        pattern = pattern_def["pattern"]
        try:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                findings.append(
                    {
                        "file": str(file_path),
                        "pattern_id": pattern_def["id"],
                        "pattern_name": pattern_def["name"],
                        "severity": pattern_def["severity"],
                        "line_num": content[: match.start()].count("\n") + 1,
                    }
                )
        except re.error:
            continue

    return findings


def scan_directory(directory=".", patterns_config="config/secret-patterns.json"):
    """Scan directory for secrets."""
    config = load_patterns(patterns_config)
    patterns = config["patterns"]
    exclusions = config.get("exclusions", {})

    findings = []
    for path in Path(directory).rglob("*"):
        if path.is_file() and not should_exclude(path, exclusions):
            results = scan_file(path, patterns, exclusions)
            findings.extend(results)

    return findings


def main():
    findings = scan_directory(".")

    if findings:
        print(f"Found {len(findings)} potential secrets:\n")
        for finding in findings:
            severity_emoji = "🔴" if finding["severity"] == "critical" else "🟠"
            print(f"{severity_emoji} [{finding['severity'].upper()}] {finding['pattern_name']}")
            print(f"   File: {finding['file']}:{finding['line_num']}")
        print("\nSecrets detected! Commit blocked.")
        return 1
    else:
        print("No secrets detected.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
