#!/usr/bin/env python3
"""Generate a compact catalog for repository AST guardrail rules."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = ROOT / "tooling" / "ast-grep" / "rules"
TESTS_DIR = ROOT / "tooling" / "ast-grep" / "rule-tests"
OUTPUT_DIR = ROOT / "docs" / "reference" / "generated"
OUTPUT_JSON = OUTPUT_DIR / "AST_RULE_CATALOG.json"
OUTPUT_MD = OUTPUT_DIR / "AST_RULE_CATALOG.md"


@dataclass(frozen=True)
class RuleRecord:
    rule_id: str
    message: str
    severity: str
    language: str
    blocking: bool
    related_issues: list[str]
    rationale_doc: str | None
    rule_file: str
    test_files: list[str]


TOP_LEVEL_FIELD_RE = re.compile(r"^(id|message|severity|language):\s*(.+?)\s*$")
COMMENT_METADATA_RE = re.compile(r"^#\s*([a-z0-9_-]+):\s*(.+?)\s*$", re.IGNORECASE)


def _parse_rule_file(path: Path) -> RuleRecord:
    fields: dict[str, str] = {}
    metadata: dict[str, str] = {}

    for line in path.read_text(encoding="utf-8").splitlines():
        comment_match = COMMENT_METADATA_RE.match(line)
        if comment_match:
            metadata[comment_match.group(1).lower()] = comment_match.group(2).strip()
            continue

        field_match = TOP_LEVEL_FIELD_RE.match(line)
        if field_match:
            fields[field_match.group(1)] = field_match.group(2).strip().strip('"')

    rule_id = fields["id"]
    test_files = sorted(
        str(test_path.relative_to(ROOT))
        for test_path in TESTS_DIR.glob(f"*{rule_id}*.yml")
    )
    related_issues = [
        issue.strip()
        for issue in metadata.get("related-issues", "").split(",")
        if issue.strip()
    ]
    blocking_value = metadata.get("blocking", "").lower()

    return RuleRecord(
        rule_id=rule_id,
        message=fields["message"],
        severity=fields["severity"],
        language=fields["language"],
        blocking=blocking_value in {"yes", "true", "blocking"} or fields["severity"] == "error",
        related_issues=related_issues,
        rationale_doc=metadata.get("rationale-doc"),
        rule_file=str(path.relative_to(ROOT)),
        test_files=test_files,
    )


def _write_json(records: list[RuleRecord]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_on": date.today().isoformat(),
        "source_dir": str(RULES_DIR.relative_to(ROOT)),
        "rules": [asdict(record) for record in records],
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(records: list[RuleRecord]) -> None:
    lines = [
        "# AST Rule Catalog",
        "",
        f"Generated on `{date.today().isoformat()}` from `{RULES_DIR.relative_to(ROOT)}`.",
        "",
        "This is a generated index of the repository's `ast-grep` structural guardrails.",
        "",
        "| Rule ID | Severity | Blocking | Related Issues | Rule File | Tests | Rationale |",
        "|---|---|---|---|---|---|---|",
    ]

    for record in records:
        related_issues = ", ".join(record.related_issues) if record.related_issues else "-"
        tests = "<br>".join(record.test_files) if record.test_files else "-"
        rationale = record.rationale_doc or "-"
        lines.append(
            "| {rule_id} | {severity} | {blocking} | {related_issues} | `{rule_file}` | {tests} | {rationale} |".format(
                rule_id=record.rule_id,
                severity=record.severity,
                blocking="yes" if record.blocking else "no",
                related_issues=related_issues,
                rule_file=record.rule_file,
                tests=tests,
                rationale=rationale,
            )
        )

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    records = sorted(
        (_parse_rule_file(path) for path in RULES_DIR.glob("*.yml")),
        key=lambda record: record.rule_id,
    )
    _write_json(records)
    _write_markdown(records)


if __name__ == "__main__":
    main()
