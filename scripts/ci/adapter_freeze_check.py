#!/usr/bin/env python3
"""STORY-266: Enforce adapter boundary freeze during consolidation.

Prevents new adapter files, wrapper files, or compatibility shims from
being added to the adapters/ directory during EPIC-069 consolidation.
Run in CI or as a pre-commit check.

Allowed adapter files are frozen at the STORY-266 baseline (2026-03-31).
To add a new adapter, update ALLOWED_FILES below and cite a story number.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Frozen baseline: every adapter file that existed on 2026-03-31.
# Adding a new file here requires a story citation in the commit message.
ALLOWED_FILES: set[str] = {
    # adapters/ root
    "adapters/__init__.py",
    "adapters/base.py",
    "adapters/constants.py",
    "adapters/instrumented.py",
    "adapters/logging.py",
    "adapters/protocols.py",
    "adapters/registry.py",
    # adapters/aggregation/
    "adapters/aggregation/__init__.py",
    # adapters/signals/
    "adapters/signals/__init__.py",
    # adapters/discovery/
    "adapters/discovery/__init__.py",
    "adapters/discovery/competitor_json.py",
    "adapters/discovery/static_catalog.py",
    "adapters/discovery/web_search.py",
    # adapters/enrichment/
    "adapters/enrichment/__init__.py",
    "adapters/enrichment/funding.py",
    "adapters/enrichment/funding_unified.py",
    "adapters/enrichment/global_market.py",
    "adapters/enrichment/linkedin.py",
    "adapters/enrichment/linkedin_unified.py",
    "adapters/enrichment/news.py",
    "adapters/enrichment/news_unified.py",
    "adapters/enrichment/patents.py",
    "adapters/enrichment/patents_unified.py",
    "adapters/enrichment/web_search_news.py",
    "adapters/enrichment/web_search_unified.py",
    "adapters/enrichment/website.py",
    "adapters/enrichment/website_unified.py",
    "adapters/enrichment/yahoo_finance.py",
}


def find_adapter_files(src_root: Path) -> list[Path]:
    """Find all Python files under src/solstein/adapters/."""
    adapters_dir = src_root / "solstein" / "adapters"
    if not adapters_dir.exists():
        return []
    return sorted(adapters_dir.rglob("*.py"))


def check_freeze(src_root: Path) -> list[str]:
    """Return list of violation messages for files outside the freeze baseline."""
    violations: list[str] = []
    for filepath in find_adapter_files(src_root):
        relative = filepath.relative_to(src_root / "solstein")
        key = str(relative)
        if key not in ALLOWED_FILES:
            violations.append(
                f"  - {filepath}: NEW adapter file not in STORY-266 baseline. "
                f"To add, update ALLOWED_FILES in adapter_freeze_check.py "
                f"and cite a story number."
            )
    return violations


def main() -> int:
    """Run the adapter freeze check."""
    src_root = Path("src")
    if not src_root.exists():
        # Try from project root
        for candidate in [Path("src"), Path(".")]:
            if (candidate / "solstein" / "adapters").exists():
                src_root = candidate
                break

    violations = check_freeze(src_root)

    if violations:
        print("STORY-266: Adapter boundary freeze violation detected!")
        print()
        print("During EPIC-069 consolidation, new adapter files are banned.")
        print("See docs/architecture/provider-scorecard.md section 4.")
        print()
        for v in violations:
            print(v)
        print()
        print("If this is intentional, update ALLOWED_FILES in this script")
        print("and cite the approving story number in your commit message.")
        return 1

    print("STORY-266: Adapter boundary freeze check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
