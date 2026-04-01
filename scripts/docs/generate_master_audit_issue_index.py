#!/usr/bin/env python3
"""Generate a deduplicated issue index from the master audit."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MASTER_AUDIT = ROOT / "docs" / "audit" / "18-03-2026_MASTER_AUDIT.md"
OUTPUT_DIR = ROOT / "docs" / "audit" / "generated"
OUTPUT_JSON = OUTPUT_DIR / "MASTER_AUDIT_ISSUE_INDEX.json"
OUTPUT_MD = OUTPUT_DIR / "MASTER_AUDIT_ISSUE_INDEX.md"


HEADING_RE = re.compile(r"^###\s+(ISSUE-\d+)(?:\s+—\s+(.+?))?\s*$")
ROW_RE = re.compile(
    r"^\|\s*(ISSUE-\d+)\s*\|\s*(.*?)\s*\|\s*`?(.*?)`?\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$"
)
METRIC_RE = re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|$")
FILE_RE = re.compile(r"^\*\*File:\*\*\s*`(.+?)`\s*$")
SEVERITY_RE = re.compile(r"^\*\*Severity:\*\*\s*(.+?)\s*$")
TITLE_RE = re.compile(r"^\*\*Title:\*\*\s*(.+?)\s*$")


def _issue_sort_key(issue_id: str) -> int:
    return int(issue_id.split("-")[1])


def _parse() -> tuple[dict[str, str], list[dict[str, object]], int, int]:
    metrics: dict[str, str] = {}
    issues: dict[str, dict[str, object]] = {}
    source_lines = MASTER_AUDIT.read_text(encoding="utf-8").splitlines()
    row_count = 0
    current_issue_id: str | None = None

    for line_number, line in enumerate(source_lines, start=1):
        metric_match = METRIC_RE.match(line)
        if metric_match:
            metrics[metric_match.group(1)] = metric_match.group(2)

        heading_match = HEADING_RE.match(line)
        if heading_match:
            issue_id, title = heading_match.groups()
            record = issues.setdefault(issue_id, {})
            record["issue_id"] = issue_id
            if title:
                record["title"] = title
            record["heading_line"] = line_number
            record.setdefault("status", "Open")
            current_issue_id = issue_id
            continue

        row_match = ROW_RE.match(line)
        if row_match:
            issue_id, summary, location, severity, status = row_match.groups()
            record = issues.setdefault(issue_id, {"issue_id": issue_id})
            row_count += 1
            record["summary"] = summary
            record["location"] = location
            record["severity"] = severity
            record["status"] = status
            record["latest_table_line"] = line_number
            record["table_occurrences"] = int(record.get("table_occurrences", 0)) + 1
            current_issue_id = issue_id
            continue

        if current_issue_id is not None:
            title_match = TITLE_RE.match(line)
            if title_match:
                issues[current_issue_id].setdefault("title", title_match.group(1))
                continue

            file_match = FILE_RE.match(line)
            if file_match:
                issues[current_issue_id].setdefault("location", file_match.group(1))
                continue

            severity_match = SEVERITY_RE.match(line)
            if severity_match:
                issues[current_issue_id].setdefault("severity", severity_match.group(1))

    issue_list = [
        {
            "issue_id": record["issue_id"],
            "title": record.get("title", record.get("summary", "")),
            "summary": record.get("summary", ""),
            "location": record.get("location", ""),
            "severity": record.get("severity", "UNKNOWN"),
            "status": record.get("status", "UNKNOWN"),
            "heading_line": record.get("heading_line"),
            "latest_table_line": record.get("latest_table_line"),
            "table_occurrences": record.get("table_occurrences", 0),
        }
        for _, record in sorted(issues.items(), key=lambda item: _issue_sort_key(item[0]))
    ]
    return metrics, issue_list, len(source_lines), row_count


def _write_json(
    metrics: dict[str, str], issue_list: list[dict[str, object]], line_count: int, row_count: int
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_on": date.today().isoformat(),
        "source_file": str(MASTER_AUDIT.relative_to(ROOT)),
        "source_line_count": line_count,
        "source_metrics": metrics,
        "parsed_issue_count": len(issue_list),
        "parsed_table_row_count": row_count,
        "notes": [
            "The audit tracker reports 284 total issues found, while the source file exposes 267 distinct ISSUE-* identifiers.",
            "The generated index follows concrete issue identifiers and preserves the source audit without rewriting its aggregate tracker totals.",
        ],
        "reconciliation_protocol": (
            "Fix-verification audits must confirm every claimed ISSUE-* fix exists in this index, "
            "reference this file in their header, and update the source audit + regenerate when status changes."
        ),
        "issues": issue_list,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(
    metrics: dict[str, str], issue_list: list[dict[str, object]], line_count: int, row_count: int
) -> None:
    lines = [
        "# Master Audit Issue Index",
        "",
        f"Generated on `{date.today().isoformat()}` from `{MASTER_AUDIT.relative_to(ROOT)}`.",
        "",
        "This is a generated, deduplicated index of issue identifiers parsed from the master audit.",
        "It does not modify the source audit. If table metadata repeats across multiple passes, the latest row is kept.",
        "",
        "## Source Snapshot",
        "",
        f"- Source line count: `{line_count}`",
        f"- Declared total issues found: `{metrics.get('Total issues found', 'unknown')}`",
        f"- Parsed distinct issue ids: `{len(issue_list)}`",
        f"- Parsed issue table rows: `{row_count}`",
        "",
        "The declared audit tracker total is higher than the distinct issue-id count because the source audit also tracks false positives, corrected entries, and pass-level aggregate accounting.",
        "",
        "## Fix-Verification Reconciliation Protocol",
        "",
        "Fix-verification audits (ad-hoc docs in `docs/audit/`) must reconcile their scope against this index.",
        "For each issue a verification audit claims to have fixed:",
        "",
        "1. Confirm the `ISSUE-*` identifier exists in the Issue Index table below.",
        "2. Reference this file by path (`docs/audit/generated/MASTER_AUDIT_ISSUE_INDEX.md`) in the verification doc header.",
        "3. If the fix changes the issue's `status`, update the source audit (`docs/audit/18-03-2026_MASTER_AUDIT.md`)",
        "   and re-run `make docs-generate` so this index reflects the new status.",
        "4. If a verification audit claims issues **not** found in this index, those are either",
        "   mislabelled (check the source audit) or new issues that need to be added to the source audit first.",
        "",
        "Machine consumers may use `docs/audit/generated/MASTER_AUDIT_ISSUE_INDEX.json` for programmatic reconciliation.",
        "",
        "## Issue Index",
        "",
        "| Issue | Severity | Status | Location | Table Rows | Title |",
        "|---|---|---|---|---|---|",
    ]

    for issue in issue_list:
        lines.append(
            "| {issue_id} | {severity} | {status} | `{location}` | {table_occurrences} | {title} |".format(
                issue_id=issue["issue_id"],
                severity=issue["severity"],
                status=issue["status"],
                location=issue["location"],
                table_occurrences=issue["table_occurrences"],
                title=issue["title"],
            )
        )

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    metrics, issue_list, line_count, row_count = _parse()
    _write_json(metrics, issue_list, line_count, row_count)
    _write_markdown(metrics, issue_list, line_count, row_count)


if __name__ == "__main__":
    main()
