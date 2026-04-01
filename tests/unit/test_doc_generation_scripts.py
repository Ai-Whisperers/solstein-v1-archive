"""Tests for documentation generation scripts.

STORY-242 (EPIC-065): AST Rule Catalog and Structural Guardrail Registry
STORY-243 (EPIC-065): Master Audit Issue Index
STORY-244 (EPIC-065): Generated Docs Freshness Enforcement
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DOCS = ROOT / "scripts" / "docs"


# ---------------------------------------------------------------------------
# STORY-242: AST Rule Catalog
# ---------------------------------------------------------------------------


def test_ast_rule_catalog_json_exists() -> None:
    """Generated AST_RULE_CATALOG.json must exist under docs/reference/generated/."""
    catalog = ROOT / "docs" / "reference" / "generated" / "AST_RULE_CATALOG.json"
    assert catalog.exists(), f"Missing generated catalog: {catalog}"


def test_ast_rule_catalog_md_exists() -> None:
    """Generated AST_RULE_CATALOG.md must exist under docs/reference/generated/."""
    catalog = ROOT / "docs" / "reference" / "generated" / "AST_RULE_CATALOG.md"
    assert catalog.exists(), f"Missing generated catalog: {catalog}"


def test_ast_rule_catalog_json_has_both_sections() -> None:
    """The JSON catalog must contain both ast_grep_rules and ci_script_gates sections."""
    catalog_path = ROOT / "docs" / "reference" / "generated" / "AST_RULE_CATALOG.json"
    assert catalog_path.exists(), "Catalog JSON not found — run make docs-generate"
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    assert "ast_grep_rules" in data, "JSON catalog missing 'ast_grep_rules' key"
    assert "ci_script_gates" in data, "JSON catalog missing 'ci_script_gates' key"


def test_ast_rule_catalog_md_has_both_sections() -> None:
    """The markdown catalog must contain sections for both ast-grep and CI script gates."""
    catalog_path = ROOT / "docs" / "reference" / "generated" / "AST_RULE_CATALOG.md"
    assert catalog_path.exists(), "Catalog MD not found — run make docs-generate"
    content = catalog_path.read_text(encoding="utf-8")
    assert "## ast-grep Rules" in content, "Markdown catalog missing 'ast-grep Rules' section"
    assert "## CI Script Gates" in content, "Markdown catalog missing 'CI Script Gates' section"


def test_ast_rule_catalog_json_blocking_gates_present() -> None:
    """Known blocking gates must appear in the CI script gates catalog."""
    catalog_path = ROOT / "docs" / "reference" / "generated" / "AST_RULE_CATALOG.json"
    assert catalog_path.exists(), "Catalog JSON not found — run make docs-generate"
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    gate_ids = {g["gate_id"] for g in data["ci_script_gates"]}
    expected_blocking = {"no-requests-in-adapters", "no-import-cycles", "generated-docs-freshness"}
    missing = expected_blocking - gate_ids
    assert not missing, f"Expected blocking gates missing from catalog: {missing}"


def test_ast_rule_catalog_guardrails_doc_reference() -> None:
    """The markdown catalog must link to the engineering guardrails guide."""
    catalog_path = ROOT / "docs" / "reference" / "generated" / "AST_RULE_CATALOG.md"
    assert catalog_path.exists(), "Catalog MD not found — run make docs-generate"
    content = catalog_path.read_text(encoding="utf-8")
    assert "guardrails.md" in content, (
        "Markdown catalog must reference the engineering guardrails guide"
    )


def test_guardrails_doc_exists() -> None:
    """docs/standards/guardrails.md must exist and reference the generated catalog."""
    doc = ROOT / "docs" / "standards" / "guardrails.md"
    assert doc.exists(), f"Missing guardrails doc: {doc}"
    content = doc.read_text(encoding="utf-8")
    assert "AST_RULE_CATALOG.md" in content, "Guardrails doc must reference AST_RULE_CATALOG.md"


def test_catalog_generator_runs_without_error() -> None:
    """generate_ast_rule_catalog.py must execute successfully."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DOCS / "generate_ast_rule_catalog.py")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, (
        f"generate_ast_rule_catalog.py failed:\n{result.stdout}\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# STORY-243: Master Audit Issue Index
# ---------------------------------------------------------------------------


def test_master_audit_index_json_exists() -> None:
    """Generated MASTER_AUDIT_ISSUE_INDEX.json must exist under docs/audit/generated/."""
    index = ROOT / "docs" / "audit" / "generated" / "MASTER_AUDIT_ISSUE_INDEX.json"
    assert index.exists(), f"Missing generated index: {index}"


def test_master_audit_index_md_exists() -> None:
    """Generated MASTER_AUDIT_ISSUE_INDEX.md must exist under docs/audit/generated/."""
    index = ROOT / "docs" / "audit" / "generated" / "MASTER_AUDIT_ISSUE_INDEX.md"
    assert index.exists(), f"Missing generated index: {index}"


def test_master_audit_index_json_has_issues() -> None:
    """The JSON index must contain a non-empty issues list."""
    index_path = ROOT / "docs" / "audit" / "generated" / "MASTER_AUDIT_ISSUE_INDEX.json"
    assert index_path.exists(), "Index JSON not found — run make docs-generate"
    data = json.loads(index_path.read_text(encoding="utf-8"))
    assert "issues" in data and len(data["issues"]) > 0, "Index JSON has no issues"


def test_master_audit_index_json_has_reconciliation_protocol() -> None:
    """The JSON index must include a reconciliation_protocol field for fix-verification audits."""
    index_path = ROOT / "docs" / "audit" / "generated" / "MASTER_AUDIT_ISSUE_INDEX.json"
    assert index_path.exists(), "Index JSON not found — run make docs-generate"
    data = json.loads(index_path.read_text(encoding="utf-8"))
    assert "reconciliation_protocol" in data, (
        "JSON index missing 'reconciliation_protocol' — fix-verification audits need this guidance"
    )
    assert len(data["reconciliation_protocol"]) > 0


def test_master_audit_index_md_has_reconciliation_section() -> None:
    """The markdown index must contain the Fix-Verification Reconciliation Protocol section."""
    index_path = ROOT / "docs" / "audit" / "generated" / "MASTER_AUDIT_ISSUE_INDEX.md"
    assert index_path.exists(), "Index MD not found — run make docs-generate"
    content = index_path.read_text(encoding="utf-8")
    assert "Fix-Verification Reconciliation Protocol" in content, (
        "Markdown index missing reconciliation protocol section"
    )


def test_master_audit_generator_runs_without_error() -> None:
    """generate_master_audit_issue_index.py must execute successfully."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DOCS / "generate_master_audit_issue_index.py")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, (
        f"generate_master_audit_issue_index.py failed:\n{result.stdout}\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# STORY-244: Generated Docs Freshness
# ---------------------------------------------------------------------------


def test_generated_docs_freshness_ci_workflow_exists() -> None:
    """The generated-docs-freshness.yml CI workflow must exist."""
    workflow = ROOT / ".github" / "workflows" / "generated-docs-freshness.yml"
    assert workflow.exists(), f"Missing CI workflow: {workflow}"


def test_generated_docs_freshness_ci_workflow_targets_develop() -> None:
    """The freshness CI workflow must trigger on PRs to develop."""
    workflow = ROOT / ".github" / "workflows" / "generated-docs-freshness.yml"
    assert workflow.exists(), "Missing CI workflow"
    content = workflow.read_text(encoding="utf-8")
    assert "develop" in content, "Freshness CI workflow must target develop branch"


def test_generated_docs_freshness_check_script_exists() -> None:
    """scripts/docs/check_generated_docs.py must exist."""
    script = ROOT / "scripts" / "docs" / "check_generated_docs.py"
    assert script.exists(), f"Missing freshness check script: {script}"


def test_generated_docs_are_fresh() -> None:
    """Committed generated docs must match a freshly-regenerated snapshot.

    This is the same check run by `make docs-generated-check` and the pre-push hook.
    If this test fails, run `make docs-generate` and commit the updated artifacts.
    """
    result = subprocess.run(
        [sys.executable, str(SCRIPTS_DOCS / "check_generated_docs.py")],
        capture_output=True,
        text=True,
        cwd=SCRIPTS_DOCS,
    )
    assert result.returncode == 0, (
        "Generated docs are stale. Run `make docs-generate` and commit the updated artifacts.\n"
        f"Output: {result.stdout}{result.stderr}"
    )
