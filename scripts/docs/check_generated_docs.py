#!/usr/bin/env python3
"""Regenerate committed docs and fail if tracked artifacts changed."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from generate_all import main as generate_all

ROOT = Path(__file__).resolve().parents[2]
TRACKED_PATHS = [
    "docs/reference/generated",
    "docs/audit/generated",
]


def main() -> None:
    generate_all()
    result = subprocess.run(
        ["git", "diff", "--quiet", "--", *TRACKED_PATHS],
        cwd=ROOT,
        check=False,
    )
    if result.returncode != 0:
        print("Generated docs are stale. Run `make docs-generate` and commit the updated artifacts.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
