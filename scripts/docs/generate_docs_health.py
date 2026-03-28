#!/usr/bin/env python3
"""Generate the docs health dashboard.

STORY-241 (EPIC-065): Aggregates documentation quality metrics from the
repository's CI gate outputs and generates a dashboard report in both
JSON and Markdown formats.

Metrics collected
-----------------
1. Quality gate violations — from check_docs_quality.py (blocking + warnings)
2. Stale docs — from check_stale_docs.py (actionable stale docs)
3. Generated docs freshness — from check_generated_docs.py (stale = fail)
4. AST rule catalog — from docs/reference/generated/AST_RULE_CATALOG.json
5. Master audit open issues — from docs/audit/generated/MASTER_AUDIT_ISSUE_INDEX.json

Output
------
- docs/reference/generated/DOCS_HEALTH.json  (machine-readable)
- docs/reference/generated/DOCS_HEALTH.md    (human-readable dashboard)

Usage
-----
    python scripts/docs/generate_docs_health.py
    python scripts/docs/generate_docs_health.py --help
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "docs" / "reference" / "generated"
OUTPUT_JSON = OUTPUT_DIR / "DOCS_HEALTH.json"
OUTPUT_MD = OUTPUT_DIR / "DOCS_HEALTH.md"

# Paths to existing generated artifacts consumed as source data
AST_CATALOG_JSON = ROOT / "docs" / "reference" / "generated" / "AST_RULE_CATALOG.json"
AUDIT_INDEX_JSON = ROOT / "docs" / "audit" / "generated" / "MASTER_AUDIT_ISSUE_INDEX.json"


# ---------------------------------------------------------------------------
# Metric collection helpers
# ---------------------------------------------------------------------------


def _collect_quality_gate_metrics() -> dict[str, object]:
    """Run check_docs_quality.py on docs/ and backlog/ and parse results."""
    script = ROOT / "scripts" / "ci" / "check_docs_quality.py"
    if not script.exists():
        return {"available": False, "error": "check_docs_quality.py not found"}

    results: dict[str, object] = {"available": True, "paths": {}}
    total_blocking = 0
    total_warnings = 0

    for path in ("docs", "backlog"):
        try:
            proc = subprocess.run(
                [sys.executable, str(script), "--path", path],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = proc.stdout + proc.stderr
            blocking = _count_in_output(output, " BLOCK ")
            warnings = _count_in_output(output, " WARN ")
            total_blocking += blocking
            total_warnings += warnings
            results["paths"][path] = {  # type: ignore[index]
                "blocking": blocking,
                "warnings": warnings,
                "exit_code": proc.returncode,
            }
        except subprocess.SubprocessError as exc:
            results["paths"][path] = {"error": str(exc)}  # type: ignore[index]

    results["total_blocking"] = total_blocking
    results["total_warnings"] = total_warnings
    results["status"] = "pass" if total_blocking == 0 else "fail"
    return results


def _collect_stale_docs_metrics() -> dict[str, object]:
    """Run check_stale_docs.py on docs/ and parse JSON output."""
    script = ROOT / "scripts" / "ci" / "check_stale_docs.py"
    if not script.exists():
        return {"available": False, "error": "check_stale_docs.py not found"}

    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--path", "docs", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        data = json.loads(proc.stdout)
        return {
            "available": True,
            "total_scanned": data.get("total_scanned", 0),
            "actionable_stale": data.get("actionable_stale_count", 0),
            "allowlisted_stale": data.get("allowlisted_stale_count", 0),
            "status": "pass" if data.get("actionable_stale_count", 0) == 0 else "warn",
        }
    except (subprocess.SubprocessError, json.JSONDecodeError, ValueError) as exc:
        return {"available": False, "error": str(exc)}


def _collect_freshness_metrics() -> dict[str, object]:
    """Run check_generated_docs.py and parse pass/fail."""
    script = ROOT / "scripts" / "docs" / "check_generated_docs.py"
    if not script.exists():
        return {"available": False, "error": "check_generated_docs.py not found"}

    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        passed = proc.returncode == 0
        return {
            "available": True,
            "status": "pass" if passed else "fail",
            "exit_code": proc.returncode,
            "detail": proc.stdout.strip()[:200] if not passed else "All generated docs are fresh.",
        }
    except subprocess.SubprocessError as exc:
        return {"available": False, "error": str(exc)}


def _collect_ast_catalog_metrics() -> dict[str, object]:
    """Read the existing AST rule catalog JSON for gate counts."""
    if not AST_CATALOG_JSON.exists():
        return {"available": False, "error": "AST_RULE_CATALOG.json not found"}

    try:
        data = json.loads(AST_CATALOG_JSON.read_text(encoding="utf-8"))
        ast_rules = data.get("ast_grep_rules", data.get("rules", []))
        script_gates = data.get("ci_script_gates", [])
        blocking_ast = sum(1 for r in ast_rules if r.get("blocking"))
        blocking_script = sum(1 for g in script_gates if g.get("blocking"))
        return {
            "available": True,
            "ast_grep_rule_count": len(ast_rules),
            "ci_script_gate_count": len(script_gates),
            "blocking_gates": blocking_ast + blocking_script,
            "generated_on": data.get("generated_on", "unknown"),
        }
    except (json.JSONDecodeError, ValueError) as exc:
        return {"available": False, "error": str(exc)}


def _collect_audit_metrics() -> dict[str, object]:
    """Read the master audit issue index for open issue counts."""
    if not AUDIT_INDEX_JSON.exists():
        return {"available": False, "error": "MASTER_AUDIT_ISSUE_INDEX.json not found"}

    try:
        data = json.loads(AUDIT_INDEX_JSON.read_text(encoding="utf-8"))
        issues = data.get("issues", [])
        open_issues = [i for i in issues if i.get("status", "").upper() in ("OPEN", "UNKNOWN", "")]
        closed_issues = [i for i in issues if i.get("status", "").upper() in ("CLOSED", "FIXED", "DONE")]
        return {
            "available": True,
            "total_issues": len(issues),
            "open_issues": len(open_issues),
            "closed_issues": len(closed_issues),
            "generated_on": data.get("generated_on", "unknown"),
        }
    except (json.JSONDecodeError, ValueError) as exc:
        return {"available": False, "error": str(exc)}


def _count_in_output(text: str, marker: str) -> int:
    return text.count(marker)


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def collect_all_metrics() -> dict[str, object]:
    today = date.today().isoformat()
    return {
        "generated_on": today,
        "quality_gate": _collect_quality_gate_metrics(),
        "stale_docs": _collect_stale_docs_metrics(),
        "freshness": _collect_freshness_metrics(),
        "ast_catalog": _collect_ast_catalog_metrics(),
        "audit_index": _collect_audit_metrics(),
    }


def _status_badge(status: str | None) -> str:
    if status == "pass":
        return "PASS"
    if status == "fail":
        return "FAIL"
    if status == "warn":
        return "WARN"
    return "N/A"


def _write_json(metrics: dict[str, object]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(metrics: dict[str, object]) -> None:
    today = metrics["generated_on"]
    qg = metrics["quality_gate"]
    sd = metrics["stale_docs"]
    fr = metrics["freshness"]
    ast = metrics["ast_catalog"]
    audit = metrics["audit_index"]

    lines = [
        "# Docs Health Dashboard",
        "",
        f"Generated on `{today}`. Updated automatically on every push to `develop` and weekly on Mondays.",
        "",
        "This dashboard aggregates metrics from the repository's documentation CI gates.",
        "See [docs/guides/docs-change-control.md](../../../guides/docs-change-control.md) for the",
        "remediation workflow.",
        "",
        "## Summary",
        "",
        "| Metric | Status | Detail |",
        "|---|---|---|",
        f"| Quality Gate (placeholders + metadata) | **{_status_badge(qg.get('status'))}** | "
        f"{qg.get('total_blocking', 'N/A')} blocking, {qg.get('total_warnings', 'N/A')} warnings |",
        f"| Stale Docs | **{_status_badge(sd.get('status'))}** | "
        f"{sd.get('actionable_stale', 'N/A')} actionable stale ({sd.get('total_scanned', 'N/A')} scanned) |",
        f"| Generated Docs Freshness | **{_status_badge(fr.get('status'))}** | "
        f"{fr.get('detail', 'N/A') if not fr.get('available') else ('Fresh' if fr.get('status') == 'pass' else fr.get('detail', 'Stale'))} |",
        f"| AST Guardrail Gates | **{'OK' if ast.get('available') else 'N/A'}** | "
        f"{ast.get('ast_grep_rule_count', 'N/A')} ast-grep rules, "
        f"{ast.get('ci_script_gate_count', 'N/A')} CI script gates, "
        f"{ast.get('blocking_gates', 'N/A')} blocking |",
        f"| Open Audit Issues | **{'OK' if audit.get('available') else 'N/A'}** | "
        f"{audit.get('open_issues', 'N/A')} open / {audit.get('total_issues', 'N/A')} total |",
        "",
        "## Remediation Links",
        "",
        "| Red/Warn Metric | Remediation |",
        "|---|---|",
        "| Quality Gate: blocking violations | Add allowlist entry — `scripts/ci/docs-quality-allowlist.json` |",
        "| Quality Gate: governance metadata | Add blockquote front-matter — see [docs-change-control.md](../../../guides/docs-change-control.md) |",
        "| Stale Docs | Review the doc or add exemption — `scripts/ci/stale-docs-allowlist.json` |",
        "| Generated Docs Freshness | Run `make docs-generate` and commit updated artifacts |",
        "| Open Audit Issues | See [MASTER_AUDIT_ISSUE_INDEX.md](MASTER_AUDIT_ISSUE_INDEX.md) |",
        "",
        "## Data Sources",
        "",
        f"- AST catalog: [AST_RULE_CATALOG.json](AST_RULE_CATALOG.json) (generated {ast.get('generated_on', 'unknown')})",
        f"- Audit index: [MASTER_AUDIT_ISSUE_INDEX.json](MASTER_AUDIT_ISSUE_INDEX.json) (generated {audit.get('generated_on', 'unknown')})",
        "- Quality gate: `scripts/ci/check_docs_quality.py`",
        "- Stale docs: `scripts/ci/check_stale_docs.py`",
        "- Freshness: `scripts/docs/check_generated_docs.py`",
        "",
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate docs health dashboard")
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Only write JSON output (skip Markdown)",
    )
    parser.parse_args(argv)

    metrics = collect_all_metrics()
    _write_json(metrics)

    parser_args = parser.parse_args(argv)
    if not parser_args.json_only:
        _write_markdown(metrics)

    try:
        json_display = OUTPUT_JSON.relative_to(ROOT)
        md_display = OUTPUT_MD.relative_to(ROOT)
    except ValueError:
        json_display = OUTPUT_JSON
        md_display = OUTPUT_MD
    print(f"[docs-health] Dashboard generated: {json_display} + {md_display}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
