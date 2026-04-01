#!/usr/bin/env python3
"""Generate a compact catalog for repository structural guardrail rules.

Covers both ast-grep YAML rules and non-ast-grep CI script gates.
"""

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
    gate_type: str = "ast-grep"


@dataclass(frozen=True)
class ScriptGateRecord:
    """A non-ast-grep structural gate implemented as a CI script."""

    gate_id: str
    description: str
    severity: str
    blocking: bool
    related_issues: list[str]
    rationale_doc: str | None
    script_file: str
    gate_type: str = "ci-script"


TOP_LEVEL_FIELD_RE = re.compile(r"^(id|message|severity|language):\s*(.+?)\s*$")
COMMENT_METADATA_RE = re.compile(r"^#\s*([a-z0-9_-]+):\s*(.+?)\s*$", re.IGNORECASE)


# Static registry of non-ast-grep structural gates.
# Add entries here whenever a new CI enforcement script is introduced.
SCRIPT_GATES: list[ScriptGateRecord] = [
    ScriptGateRecord(
        gate_id="no-requests-in-adapters",
        description="Ban `import requests` in adapter and agent modules — all HTTP must use httpx (async-safe).",
        severity="error",
        blocking=True,
        related_issues=["STORY-136"],
        rationale_doc="docs/developers/async-http-guidelines.md",
        script_file="scripts/ci/check_banned_imports.py",
    ),
    ScriptGateRecord(
        gate_id="no-import-cycles",
        description="Detect circular import chains between Python modules — cycles break strict typing and generated docs.",
        severity="error",
        blocking=True,
        related_issues=["EPIC-066"],
        rationale_doc=None,
        script_file="scripts/ci/detect_import_cycles.py",
    ),
    ScriptGateRecord(
        gate_id="file-size-limit",
        description="Enforce max 500-line Python files; files over the limit are flagged as architecture debt.",
        severity="warning",
        blocking=False,
        related_issues=[],
        rationale_doc=".claude/rules/code-quality.md",
        script_file="scripts/ci/check_file_sizes.py",
    ),
    ScriptGateRecord(
        gate_id="function-size-limit",
        description="Enforce max 100-line functions; god-functions must be split per project rules.",
        severity="warning",
        blocking=False,
        related_issues=[],
        rationale_doc=".claude/rules/code-quality.md",
        script_file="scripts/ci/check_function_sizes.py",
    ),
    ScriptGateRecord(
        gate_id="class-size-limit",
        description="Enforce max 300-line classes; god-classes must be extracted into focused modules.",
        severity="warning",
        blocking=False,
        related_issues=[],
        rationale_doc=".claude/rules/code-quality.md",
        script_file="scripts/ci/check_class_sizes.py",
    ),
    ScriptGateRecord(
        gate_id="code-smell-detection",
        description="Detect bare-except, broad-exception, and other structural smells via AST scan.",
        severity="warning",
        blocking=False,
        related_issues=[],
        rationale_doc=".claude/rules/error-handling.md",
        script_file="scripts/ci/code_smell_detector.py",
    ),
    ScriptGateRecord(
        gate_id="dead-code-detection",
        description="Identify modules and symbols with zero instantiation sites — candidates for deletion.",
        severity="warning",
        blocking=False,
        related_issues=["EPIC-037"],
        rationale_doc=None,
        script_file="scripts/ci/detect_dead_code.py",
    ),
    ScriptGateRecord(
        gate_id="generated-docs-freshness",
        description=(
            "Fail CI when committed generated docs differ from a freshly-regenerated snapshot — "
            "prevents stale catalogs and audit indexes from being merged."
        ),
        severity="error",
        blocking=True,
        related_issues=["STORY-244"],
        rationale_doc="docs/governance/docs-topology.md",
        script_file="scripts/docs/check_generated_docs.py",
    ),
]


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


def _write_json(
    ast_records: list[RuleRecord],
    script_gates: list[ScriptGateRecord],
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_on": date.today().isoformat(),
        "source_dir": str(RULES_DIR.relative_to(ROOT)),
        "ast_grep_rules": [asdict(record) for record in ast_records],
        "ci_script_gates": [asdict(gate) for gate in script_gates],
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(
    ast_records: list[RuleRecord],
    script_gates: list[ScriptGateRecord],
) -> None:
    lines = [
        "# AST Rule Catalog and Structural Guardrail Registry",
        "",
        f"Generated on `{date.today().isoformat()}` from `{RULES_DIR.relative_to(ROOT)}`.",
        "",
        (
            "This catalog covers all structural guardrails enforced in this repository — "
            "both `ast-grep` YAML rules and non-ast-grep CI script gates."
        ),
        "",
        "See also: [Engineering Guardrails Guide](../../standards/guardrails.md)",
        "",
        "---",
        "",
        "## ast-grep Rules",
        "",
        "Pattern-based structural checks enforced at PR time via `npm run ast-grep`.",
        "",
        "| Rule ID | Severity | Blocking | Related Issues | Rule File | Tests | Rationale |",
        "|---|---|---|---|---|---|---|",
    ]

    for record in ast_records:
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

    lines += [
        "",
        "---",
        "",
        "## CI Script Gates",
        "",
        "Non-ast-grep structural checks enforced by Python scripts in `scripts/ci/` or `scripts/docs/`.",
        "",
        "| Gate ID | Severity | Blocking | Related Issues | Script | Rationale |",
        "|---|---|---|---|---|---|",
    ]

    for gate in script_gates:
        related_issues = ", ".join(gate.related_issues) if gate.related_issues else "-"
        rationale = gate.rationale_doc or "-"
        lines.append(
            "| {gate_id} | {severity} | {blocking} | {related_issues} | `{script_file}` | {rationale} |".format(
                gate_id=gate.gate_id,
                severity=gate.severity,
                blocking="yes" if gate.blocking else "no",
                related_issues=related_issues,
                script_file=gate.script_file,
                rationale=rationale,
            )
        )

    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ast_records = sorted(
        (_parse_rule_file(path) for path in RULES_DIR.glob("*.yml")),
        key=lambda record: record.rule_id,
    )
    script_gates = sorted(SCRIPT_GATES, key=lambda g: g.gate_id)
    _write_json(ast_records, script_gates)
    _write_markdown(ast_records, script_gates)


if __name__ == "__main__":
    main()
