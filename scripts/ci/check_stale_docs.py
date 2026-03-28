#!/usr/bin/env python3
"""Stale-doc detector: identify docs that have exceeded their review interval.

STORY-239 (EPIC-065): Implements staleness detection for docs/ and backlog/.

Staleness is determined by the age of the file's last git commit. Policy is
defined per document class in `scripts/ci/stale-docs-policy.json`. Ownership
is resolved from the same config file and used to route alert output.

Allowlist format
----------------
Exceptions are declared in `scripts/ci/stale-docs-allowlist.json`.
Every entry MUST include:
  - owner: str — responsible team or person
  - rationale: str — why staleness policy does not apply
  - expiry: str — ISO date or milestone when the exception should be removed
  - file: str (optional) — exact relative path to exempt
  - file_prefix: str (optional) — exempt all files under this prefix

Output modes
------------
- Console: human-readable table grouped by owner team
- JSON (--json): machine-readable for CI integration and dashboard ingestion
- Exit code 1 if blocking stale docs exist AND --fail flag is set

Usage
-----
    python scripts/ci/check_stale_docs.py [--path docs] [--fail] [--json]
    python scripts/ci/check_stale_docs.py --help

Exit codes
----------
    0 — No stale docs (or --fail not set)
    1 — Stale docs found AND --fail flag is set
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "scripts" / "ci" / "stale-docs-policy.json"
ALLOWLIST_PATH = ROOT / "scripts" / "ci" / "stale-docs-allowlist.json"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class DocClassPolicy:
    class_id: str
    description: str
    path_prefixes: list[str]
    max_age_days: int
    owner_team: str
    escalation_owner: str


@dataclass
class StaleDoc:
    file: str
    last_modified: str  # ISO date string
    age_days: int
    max_age_days: int
    class_id: str
    owner_team: str
    allowlisted: bool = False
    allowlist_rationale: str = ""


@dataclass
class StalenessReport:
    generated_on: str
    search_root: str
    stale: list[StaleDoc] = field(default_factory=list)
    exempt: list[StaleDoc] = field(default_factory=list)
    total_scanned: int = 0

    @property
    def actionable(self) -> list[StaleDoc]:
        return [d for d in self.stale if not d.allowlisted]

    @property
    def allowlisted(self) -> list[StaleDoc]:
        return [d for d in self.stale if d.allowlisted]


# ---------------------------------------------------------------------------
# Policy + allowlist loading
# ---------------------------------------------------------------------------


def _load_policy() -> tuple[list[DocClassPolicy], dict[str, str], str]:
    """Return (classes, ownership_map, unowned_owner)."""
    if not POLICY_PATH.exists():
        return [], {}, "platform-team"
    raw = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    classes = [DocClassPolicy(**c) for c in raw.get("classes", [])]
    ownership_map: dict[str, str] = raw.get("ownership_map", {})
    unowned_owner: str = raw.get("escalation", {}).get("unowned_owner", "platform-team")
    return classes, ownership_map, unowned_owner


def _load_allowlist() -> list[dict[str, str]]:
    if not ALLOWLIST_PATH.exists():
        return []
    return json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))


def _is_allowlisted(file_rel: str, allowlist: list[dict[str, str]]) -> tuple[bool, str]:
    """Return (is_exempt, rationale)."""
    for entry in allowlist:
        exact = entry.get("file", "")
        prefix = entry.get("file_prefix", "")
        if exact and exact == file_rel:
            return True, entry.get("rationale", "")
        if prefix and file_rel.startswith(prefix):
            return True, entry.get("rationale", "")
    return False, ""


# ---------------------------------------------------------------------------
# Git-based age detection
# ---------------------------------------------------------------------------


def _git_last_modified(path: Path) -> date | None:
    """Return the date of the last git commit touching this file, or None."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", "--", str(path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        line = result.stdout.strip()
        if not line:
            return None
        return date.fromisoformat(line[:10])
    except (subprocess.SubprocessError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Class resolution
# ---------------------------------------------------------------------------


def _resolve_class(file_rel: str, classes: list[DocClassPolicy]) -> DocClassPolicy | None:
    """Return the most specific matching class, or None if no match."""
    best: DocClassPolicy | None = None
    best_prefix_len = -1
    for cls in classes:
        for prefix in cls.path_prefixes:
            if file_rel.startswith(prefix) and len(prefix) > best_prefix_len:
                best = cls
                best_prefix_len = len(prefix)
    return best


def _resolve_owner(file_rel: str, ownership_map: dict[str, str], unowned_owner: str) -> str:
    best_owner = unowned_owner
    best_prefix_len = -1
    for prefix, owner in ownership_map.items():
        if file_rel.startswith(prefix) and len(prefix) > best_prefix_len:
            best_owner = owner
            best_prefix_len = len(prefix)
    return best_owner


# ---------------------------------------------------------------------------
# Core scan
# ---------------------------------------------------------------------------


def run_scan(search_root: Path) -> StalenessReport:
    classes, ownership_map, unowned_owner = _load_policy()
    allowlist = _load_allowlist()
    today = date.today()

    report = StalenessReport(
        generated_on=today.isoformat(),
        search_root=str(search_root.relative_to(ROOT)),
    )

    for path in sorted(search_root.rglob("*.md")):
        try:
            file_rel = str(path.relative_to(ROOT))
        except ValueError:
            file_rel = str(path)

        report.total_scanned += 1

        cls = _resolve_class(file_rel, classes)
        if cls is None:
            continue  # No policy applies — skip

        # Skip generated docs — their freshness is enforced by a separate gate
        if "generated" in file_rel:
            continue

        last_modified = _git_last_modified(path)
        if last_modified is None:
            # Untracked file — skip; not yet committed
            continue

        age_days = (today - last_modified).days
        if age_days <= cls.max_age_days:
            continue  # Not stale

        owner = _resolve_owner(file_rel, ownership_map, unowned_owner)
        is_exempt, rationale = _is_allowlisted(file_rel, allowlist)

        doc = StaleDoc(
            file=file_rel,
            last_modified=last_modified.isoformat(),
            age_days=age_days,
            max_age_days=cls.max_age_days,
            class_id=cls.class_id,
            owner_team=owner,
            allowlisted=is_exempt,
            allowlist_rationale=rationale,
        )
        report.stale.append(doc)

    return report


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------


def _print_report(report: StalenessReport, verbose: bool = False) -> None:
    actionable = report.actionable
    exempt = report.allowlisted

    if not actionable and not exempt:
        print(
            f"[stale-docs] OK — {report.total_scanned} docs scanned, none stale."
        )
        return

    if exempt:
        print(f"[stale-docs] {len(exempt)} allowlisted stale doc(s) (not actionable):")
        for doc in sorted(exempt, key=lambda d: d.owner_team):
            print(f"  EXEMPT  [{doc.owner_team}] {doc.file} — {doc.age_days}d old (limit {doc.max_age_days}d)")

    if actionable:
        # Group by owner team
        by_owner: dict[str, list[StaleDoc]] = {}
        for doc in actionable:
            by_owner.setdefault(doc.owner_team, []).append(doc)

        print(
            f"\n[stale-docs] {len(actionable)} actionable stale doc(s) "
            f"(grouped by owner):\n"
        )
        for owner in sorted(by_owner):
            docs = sorted(by_owner[owner], key=lambda d: -d.age_days)
            print(f"  {owner}:")
            for doc in docs:
                overdue = doc.age_days - doc.max_age_days
                print(
                    f"    STALE  {doc.file}\n"
                    f"           last modified: {doc.last_modified}  "
                    f"age: {doc.age_days}d  limit: {doc.max_age_days}d  "
                    f"overdue by: {overdue}d  class: {doc.class_id}"
                )
        print(
            "\nTo suppress a false positive, add an entry to "
            "scripts/ci/stale-docs-allowlist.json with 'owner', 'rationale', "
            "'expiry', and 'file' or 'file_prefix' fields."
        )
    else:
        print(f"\n[stale-docs] OK — {report.total_scanned} docs scanned, 0 actionable stale docs.")


def _print_json(report: StalenessReport) -> None:
    payload = {
        "generated_on": report.generated_on,
        "search_root": report.search_root,
        "total_scanned": report.total_scanned,
        "actionable_stale_count": len(report.actionable),
        "allowlisted_stale_count": len(report.allowlisted),
        "actionable": [asdict(d) for d in report.actionable],
        "allowlisted": [asdict(d) for d in report.allowlisted],
    }
    print(json.dumps(payload, indent=2))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stale-doc detector")
    parser.add_argument(
        "--path",
        default="docs",
        help="Directory to scan (default: docs)",
    )
    parser.add_argument(
        "--fail",
        action="store_true",
        help="Exit 1 if actionable stale docs are found",
    )
    parser.add_argument(
        "--json",
        dest="json_output",
        action="store_true",
        help="Output machine-readable JSON instead of human-readable text",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show additional detail for each stale doc",
    )
    args = parser.parse_args(argv)

    search_root = ROOT / args.path
    if not search_root.exists():
        print(f"ERROR: search path does not exist: {search_root}", file=sys.stderr)
        return 1

    report = run_scan(search_root)

    if args.json_output:
        _print_json(report)
    else:
        _print_report(report, verbose=args.verbose)

    if args.fail and report.actionable:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
