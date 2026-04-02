#!/usr/bin/env python3
"""Generate the documentation health dashboard."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "docs" / "reference" / "generated"
OUTPUT_JSON = OUTPUT_DIR / "DOCS_HEALTH.json"
OUTPUT_MD = OUTPUT_DIR / "DOCS_HEALTH.md"
AST_CATALOG_JSON = OUTPUT_DIR / "AST_RULE_CATALOG.json"
AUDIT_INDEX_JSON = ROOT / "docs" / "audit" / "generated" / "MASTER_AUDIT_ISSUE_INDEX.json"
STALE_REPORT_JSON = Path("/tmp/stale-docs-report.json")


def _load_module(module_name: str, path: Path) -> Any | None:
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _status_badge(status: str | None) -> str:
    if status == "pass":
        return "PASS"
    if status == "fail":
        return "FAIL"
    if status == "warn":
        return "WARN"
    return "N/A"


def _collect_quality_gate_metrics() -> dict[str, Any]:
    script_path = ROOT / "scripts" / "ci" / "check_docs_quality.py"
    module = _load_module("check_docs_quality", script_path)
    if module is None:
        return {"available": False, "error": f"Missing script: {script_path}"}

    paths: dict[str, dict[str, int]] = {}
    total_blocking = 0
    total_warnings = 0

    for doc_path in ("docs", "backlog"):
        result = module.check_quality(str(ROOT / doc_path), strict=False)
        violations = result.get("violations", [])
        blocking = sum(1 for violation in violations if violation.get("type") == "placeholder")
        warnings = len(violations) - blocking
        paths[doc_path] = {
            "exit_code": 1 if blocking else 0,
            "blocking": blocking,
            "warnings": warnings,
        }
        total_blocking += blocking
        total_warnings += warnings

    if total_blocking:
        status = "fail"
    elif total_warnings:
        status = "warn"
    else:
        status = "pass"

    return {
        "available": True,
        "status": status,
        "paths": paths,
        "total_blocking": total_blocking,
        "total_warnings": total_warnings,
    }


def _collect_stale_docs_metrics() -> dict[str, Any]:
    script_path = ROOT / "scripts" / "ci" / "check_stale_docs.py"
    if not script_path.exists():
        return {"available": False, "error": f"Missing script: {script_path}"}

    try:
        result = subprocess.run(
            ["python3", str(script_path), "--path", "docs", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        return {"available": False, "error": str(exc)}

    payload: dict[str, Any] | None = None
    stdout = result.stdout.strip()
    if stdout:
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            payload = None

    if payload is None and STALE_REPORT_JSON.exists():
        try:
            payload = json.loads(STALE_REPORT_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            return {"available": False, "error": str(exc)}

    if payload is None:
        return {"available": False, "error": "No stale-docs report produced"}

    actionable = int(payload.get("actionable_stale_count", 0))
    return {
        "available": True,
        "status": "fail" if actionable else "pass",
        "total_scanned": int(payload.get("total_scanned", 0)),
        "allowlisted_stale": int(payload.get("allowlisted_stale_count", 0)),
        "actionable_stale": actionable,
    }


def _collect_freshness_metrics() -> dict[str, Any]:
    script_path = ROOT / "scripts" / "docs" / "check_generated_docs.py"
    if not script_path.exists():
        return {"available": False, "error": f"Missing script: {script_path}"}

    try:
        result = subprocess.run(
            ["python3", str(script_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except subprocess.TimeoutExpired as exc:
        return {"available": False, "error": str(exc)}
    except (subprocess.SubprocessError, OSError) as exc:
        return {"available": False, "error": str(exc)}

    if result.returncode == 0:
        return {"available": True, "status": "pass"}
    if result.returncode == 1:
        return {"available": True, "status": "fail"}
    return {
        "available": False,
        "error": (result.stderr or result.stdout or f"exit {result.returncode}").strip(),
    }


def _collect_ast_catalog_metrics() -> dict[str, Any]:
    if not AST_CATALOG_JSON.exists():
        return {"available": False, "error": f"Missing catalog: {AST_CATALOG_JSON}"}

    payload = json.loads(AST_CATALOG_JSON.read_text(encoding="utf-8"))
    ast_rules = payload.get("ast_grep_rules", [])
    ci_gates = payload.get("ci_script_gates", [])
    blocking_gates = sum(1 for gate in [*ast_rules, *ci_gates] if gate.get("blocking"))

    return {
        "available": True,
        "generated_on": payload.get("generated_on"),
        "ast_grep_rule_count": len(ast_rules),
        "ci_script_gate_count": len(ci_gates),
        "blocking_gates": blocking_gates,
    }


def _collect_audit_metrics() -> dict[str, Any]:
    if not AUDIT_INDEX_JSON.exists():
        return {"available": False, "error": f"Missing audit index: {AUDIT_INDEX_JSON}"}

    payload = json.loads(AUDIT_INDEX_JSON.read_text(encoding="utf-8"))
    issues = payload.get("issues", [])
    open_issues = sum(1 for issue in issues if str(issue.get("status", "")).lower() == "open")
    total_issues = len(issues)

    return {
        "available": True,
        "generated_on": payload.get("generated_on"),
        "total_issues": total_issues,
        "open_issues": open_issues,
        "closed_issues": total_issues - open_issues,
    }


def collect_all_metrics(*, skip_freshness: bool = False) -> dict[str, Any]:
    freshness = (
        {"available": False, "status": None, "error": "Skipped during aggregate docs generation to avoid recursion"}
        if skip_freshness
        else _collect_freshness_metrics()
    )
    return {
        "generated_on": date.today().isoformat(),
        "quality_gate": _collect_quality_gate_metrics(),
        "stale_docs": _collect_stale_docs_metrics(),
        "freshness": freshness,
        "ast_catalog": _collect_ast_catalog_metrics(),
        "audit_index": _collect_audit_metrics(),
    }


def _render_markdown(metrics: dict[str, Any]) -> str:
    quality_gate = metrics["quality_gate"]
    stale_docs = metrics["stale_docs"]
    freshness = metrics["freshness"]
    ast_catalog = metrics["ast_catalog"]
    audit_index = metrics["audit_index"]

    freshness_detail = _status_badge(freshness.get("status"))
    if freshness.get("available"):
        freshness_summary = freshness_detail
    else:
        freshness_summary = "N/A"

    lines = [
        "# Docs Health Dashboard",
        "",
        (
            f"Generated on `{metrics['generated_on']}`. Updated automatically on every push to `develop` "
            "and weekly on Mondays."
        ),
        "",
        "This dashboard aggregates metrics from the repository's documentation CI gates.",
        "See [docs/guides/docs-change-control.md](../../../guides/docs-change-control.md) for the",
        "remediation workflow.",
        "",
        "## Summary",
        "",
        "| Metric | Status | Detail |",
        "|---|---|---|",
        (
            f"| Quality Gate (placeholders + metadata) | **{_status_badge(quality_gate.get('status'))}** | "
            f"{quality_gate.get('total_blocking', 0)} blocking, {quality_gate.get('total_warnings', 0)} warnings |"
        ),
        (
            f"| Stale Docs | **{_status_badge(stale_docs.get('status'))}** | "
            f"{stale_docs.get('actionable_stale', 0)} actionable stale ({stale_docs.get('total_scanned', 0)} scanned) |"
        ),
        f"| Generated Docs Freshness | **{freshness_summary}** | {freshness_summary} |",
        (
            f"| AST Guardrail Gates | **OK** | {ast_catalog.get('ast_grep_rule_count', 0)} ast-grep rules, "
            f"{ast_catalog.get('ci_script_gate_count', 0)} CI script gates, "
            f"{ast_catalog.get('blocking_gates', 0)} blocking |"
        ),
        (
            f"| Open Audit Issues | **OK** | {audit_index.get('open_issues', 0)} open / "
            f"{audit_index.get('total_issues', 0)} total |"
        ),
        "",
        "## Remediation Links",
        "",
        "| Red/Warn Metric | Remediation |",
        "|---|---|",
        "| Quality Gate: blocking violations | Add allowlist entry - `scripts/ci/docs-quality-allowlist.json` |",
        (
            "| Quality Gate: governance metadata | Add blockquote front-matter - see "
            "[docs-change-control.md](../../../guides/docs-change-control.md) |"
        ),
        "| Stale Docs | Review the doc or add exemption - `scripts/ci/stale-docs-allowlist.json` |",
        "| Generated Docs Freshness | Run `make docs-generate` and commit updated artifacts |",
        "| Open Audit Issues | See [MASTER_AUDIT_ISSUE_INDEX.md](../../../audit/generated/MASTER_AUDIT_ISSUE_INDEX.md) |",
        "",
        "## Data Sources",
        "",
        (
            f"- AST catalog: [AST_RULE_CATALOG.json](AST_RULE_CATALOG.json) "
            f"(generated {ast_catalog.get('generated_on', 'unknown')})"
        ),
        (
            f"- Audit index: [MASTER_AUDIT_ISSUE_INDEX.json](../../../audit/generated/MASTER_AUDIT_ISSUE_INDEX.json) "
            f"(generated {audit_index.get('generated_on', 'unknown')})"
        ),
        "- Quality gate: `scripts/ci/check_docs_quality.py`",
        "- Stale docs: `scripts/ci/check_stale_docs.py`",
        "- Freshness: `scripts/docs/check_generated_docs.py`",
        "",
    ]
    return "\n".join(lines)


def _write_outputs(metrics: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(_render_markdown(metrics), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the documentation health dashboard")
    parser.add_argument(
        "--skip-freshness",
        action="store_true",
        help="Skip freshness validation to avoid recursive generation during aggregate docs refresh",
    )
    args = parser.parse_args(argv)

    metrics = collect_all_metrics(skip_freshness=args.skip_freshness)
    _write_outputs(metrics)
    print(f"Generated docs health dashboard: {OUTPUT_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
