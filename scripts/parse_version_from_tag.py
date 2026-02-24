#!/usr/bin/env python3
"""Parse version from git tags."""

import re
import subprocess
import sys


TAG_PATTERNS = {
    "release": r"^release-(\d+\.\d+\.\d+)(?:-rc(\d+))?$",
    "test": r"^test-(\d+\.\d+\.\d+)-rc(\d+)$",
    "coverage": r"^coverage-(\d+\.\d+\.\d+)$",
    "security": r"^security-(\d{8})$",
}


def get_latest_tag():
    """Get the latest git tag."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def parse_tag(tag):
    """Parse tag and extract version info."""
    if not tag:
        return None

    for tag_type, pattern in TAG_PATTERNS.items():
        match = re.match(pattern, tag)
        if match:
            if tag_type == "release":
                rc = match.group(2)
                return {
                    "type": tag_type,
                    "version": match.group(1),
                    "rc": f"rc{rc}" if rc else None,
                    "full_version": f"{match.group(1)}-rc{rc}" if rc else match.group(1),
                }
            elif tag_type == "test":
                return {
                    "type": tag_type,
                    "version": match.group(1),
                    "rc": f"rc{match.group(2)}",
                    "full_version": f"{match.group(1)}-test-{match.group(2)}",
                }
            elif tag_type == "coverage":
                return {
                    "type": tag_type,
                    "version": match.group(1),
                    "rc": None,
                    "full_version": f"{match.group(1)}",
                }
            elif tag_type == "security":
                return {
                    "type": tag_type,
                    "version": f"0.0.1-security-{match.group(1)}",
                    "rc": None,
                    "full_version": f"0.0.1-security-{match.group(1)}",
                }

    return None


def main():
    tag = get_latest_tag()
    parsed = parse_tag(tag)

    if parsed:
        print(f"Tag: {tag}")
        print(f"Type: {parsed['type']}")
        print(f"Version: {parsed['version']}")
        if parsed["rc"]:
            print(f"Pre-release: {parsed['rc']}")
        return 0
    else:
        print("No version tag found")
        return 1


if __name__ == "__main__":
    sys.exit(main())
