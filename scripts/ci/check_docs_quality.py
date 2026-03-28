#!/usr/bin/env python3
"""CI docs quality gate: placeholder tokens, metadata validation.

STORY-238 (EPIC-065): Implements the docs quality gate that runs on every
PR touching docs/ or backlog/. Checks:

1. Placeholder tokens — patterns that signal unfinished content
2. Metadata validation — governance docs must have required front-matter keys

Broken-link checking is handled separately by the existing link-allowlist
machinery (STORY-234/EPIC-064).

Severity tiers
--------------
- blocking: Check fails CI. Use for structural violations that introduce
  concrete risk (e.g. tokens that signal unfinished security docs).
- warn:     Check emits a warning but does not fail CI. Use for style
            issues or patterns that may be intentional in some contexts.

Allowlist format
----------------
Exceptions are declared in `scripts/ci/docs-quality-allowlist.json`.
Every allowlist entry MUST include:
  - owner: str — person or team responsible for the exception
  - rationale: str — why this exception exists
  - expiry: str — ISO date or milestone when the exception should be removed
  - pattern: str — the exact text or pattern that is allowlisted
  - file: str (optional) — restrict to a specific file; omit to apply globally

Usage
-----
    python scripts/ci/check_docs_quality.py [--path docs] [--strict]
    python scripts/ci/check_docs_quality.py --help

Exit codes
----------
    0 — No blocking violations
    1 — One or more blocking violations found
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = ROOT / "scripts" / "ci" / "docs-quality-allowlist.json"

# ---------------------------------------------------------------------------
# Placeholder token patterns
# ---------------------------------------------------------------------------

BLOCKING_TOKENS: list[tuple[str, re.Pattern[str]]] = [
    ("UNFILLED_TEMPLATE_VARIABLE", re.compile(r"\{\{[^}]+\}\}")),
    ("PLACEHOLDER_MARKER", re.compile(r"\bPLACEHOLDER\b")),
    ("TODO_IN_GOVERNANCE_DOC", re.compile(r"\bTODO\s*:")),
    ("FIXME_IN_GOVERNANCE_DOC", re.compile(r"\bFIXME\s*:")),
]

WARNING_TOKENS: list[tuple[str, re.Pattern[str]]] = [
    ("TBD_MARKER", re.compile(r"\bTBD\b")),
    ("LOREM_IPSUM", re.compile(r"\blorem\s+ipsum\b", re.IGNORECASE)),
    ("EXAMPLE_COM", re.compile(r"https?://example\.com")),
]

# ---------------------------------------------------------------------------
# Metadata (front-matter) requirements for governance docs
# ---------------------------------------------------------------------------

# Governance docs are in docs/governance/ and docs/standards/ — they must
# have the blockquote front-matter established in STORY-233 (EPIC-063).
GOVERNANCE_DIRS = {"docs/governance", "docs/standards"}

REQUIRED_METADATA_KEYS = ["Status", "Owner", "Last Reviewed", "Superseded By"]
WARNING_METADATA_KEYS = ["Review Cadence"]

BLOCKQUOTE_METADATA_RE = re.compile(r"^\s*>\s+\*\*(.+?)\*\*\s*:", re.MULTILINE)


@dataclass
class Violation:
    file: str
    line: int
    check: str
    severity: str  # "blocking" | "warn"
    message: str
    allowlisted: bool = False


@dataclass
class CheckResult:
    violations: list[Violation] = field(default_factory=list)

    @property
    def blocking(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == "blocking" and not v.allowlisted]

    @property
    def warnings(self) -> list[Violation]:
        return [v for v in self.violations if v.severity == "warn" and not v.allowlisted]


def _load_allowlist() -> list[dict[str, str]]:
    if not ALLOWLIST_PATH.exists():
        return []
    return json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))


def _is_allowlisted(
    file_rel: str,
    pattern_str: str,
    allowlist: list[dict[str, str]],
) -> bool:
    for entry in allowlist:
        entry_file = entry.get("file", "")
        if entry_file and entry_file != file_rel:
            continue
        if entry.get("pattern", "") == pattern_str:
            return True
    return False


def _check_placeholder_tokens(
    path: Path,
    file_rel: str,
    allowlist: list[dict[str, str]],
) -> list[Violation]:
    violations: list[Violation] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return violations

    for lineno, line in enumerate(lines, start=1):
        for check_id, pattern in BLOCKING_TOKENS:
            for match in pattern.finditer(line):
                token = match.group(0)
                allowlisted = _is_allowlisted(file_rel, token, allowlist)
                violations.append(
                    Violation(
                        file=file_rel,
                        line=lineno,
                        check=check_id,
                        severity="blocking",
                        message=f"Placeholder token '{token}' found in committed doc",
                        allowlisted=allowlisted,
                    )
                )

        for check_id, pattern in WARNING_TOKENS:
            for match in pattern.finditer(line):
                token = match.group(0)
                allowlisted = _is_allowlisted(file_rel, token, allowlist)
                violations.append(
                    Violation(
                        file=file_rel,
                        line=lineno,
                        check=check_id,
                        severity="warn",
                        message=f"Draft marker '{token}' found — verify this is intentional",
                        allowlisted=allowlisted,
                    )
                )
    return violations


def _check_metadata(
    path: Path,
    file_rel: str,
    allowlist: list[dict[str, str]],
) -> list[Violation]:
    """Check governance docs for required blockquote front-matter keys."""
    violations: list[Violation] = []
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return violations

    found_keys = set(
        m.group(1)
        for m in BLOCKQUOTE_METADATA_RE.finditer(content)
    )

    for key in REQUIRED_METADATA_KEYS:
        if key not in found_keys:
            allowlisted = _is_allowlisted(file_rel, f"missing:{key}", allowlist)
            violations.append(
                Violation(
                    file=file_rel,
                    line=0,
                    check="MISSING_REQUIRED_METADATA",
                    severity="blocking",
                    message=f"Governance doc missing required front-matter key: **{key}**",
                    allowlisted=allowlisted,
                )
            )

    for key in WARNING_METADATA_KEYS:
        if key not in found_keys:
            allowlisted = _is_allowlisted(file_rel, f"missing:{key}", allowlist)
            violations.append(
                Violation(
                    file=file_rel,
                    line=0,
                    check="MISSING_RECOMMENDED_METADATA",
                    severity="warn",
                    message=f"Governance doc missing recommended front-matter key: **{key}**",
                    allowlisted=allowlisted,
                )
            )

    return violations


def _is_governance_doc(file_rel: str) -> bool:
    return any(file_rel.startswith(d + "/") for d in GOVERNANCE_DIRS)


def run_checks(search_root: Path) -> CheckResult:
    result = CheckResult()
    allowlist = _load_allowlist()

    for path in sorted(search_root.rglob("*.md")):
        try:
            file_rel = str(path.relative_to(ROOT))
        except ValueError:
            file_rel = str(path)

        # Skip generated docs — they're controlled by the freshness gate
        if "generated" in file_rel:
            continue

        result.violations.extend(
            _check_placeholder_tokens(path, file_rel, allowlist)
        )

        if _is_governance_doc(file_rel):
            result.violations.extend(
                _check_metadata(path, file_rel, allowlist)
            )

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Docs quality gate")
    parser.add_argument(
        "--path",
        default="docs",
        help="Directory to scan (default: docs)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as blocking violations",
    )
    args = parser.parse_args(argv)

    search_root = ROOT / args.path
    if not search_root.exists():
        print(f"ERROR: search path does not exist: {search_root}", file=sys.stderr)
        return 1

    result = run_checks(search_root)

    # Summarize warnings
    if result.warnings:
        print(f"[docs-quality] {len(result.warnings)} warning(s):")
        for v in result.warnings:
            loc = f"{v.file}:{v.line}" if v.line else v.file
            print(f"  WARN  {v.check} @ {loc}: {v.message}")

    # Summarize blocking violations
    blocking = result.blocking
    if args.strict:
        blocking = blocking + result.warnings

    if blocking:
        print(f"\n[docs-quality] {len(blocking)} blocking violation(s):")
        for v in blocking:
            loc = f"{v.file}:{v.line}" if v.line else v.file
            print(f"  BLOCK {v.check} @ {loc}: {v.message}")
        print(
            "\nTo allowlist a violation, add an entry to scripts/ci/docs-quality-allowlist.json "
            "with 'owner', 'rationale', 'expiry', and 'pattern' fields."
        )
        return 1

    print(f"[docs-quality] OK — {len(result.warnings)} warnings, 0 blocking violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
