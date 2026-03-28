"""Tests for scripts/docs/generate_docs_health.py (STORY-241).

Covers:
- Metric collection helpers return expected structure when sub-scripts unavailable
- collect_all_metrics assembles all sections
- JSON and Markdown outputs are generated and parseable
- CI workflow and Makefile target existence
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import mock

import pytest

_SCRIPTS_DOCS = Path(__file__).resolve().parents[2] / "scripts" / "docs"
if str(_SCRIPTS_DOCS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DOCS))

import generate_docs_health as _gdh
from generate_docs_health import (
    OUTPUT_JSON,
    OUTPUT_MD,
    _collect_ast_catalog_metrics,
    _collect_audit_metrics,
    _collect_freshness_metrics,
    _collect_quality_gate_metrics,
    _collect_stale_docs_metrics,
    _status_badge,
    collect_all_metrics,
    main,
)

# ---------------------------------------------------------------------------
# Status badge helper
# ---------------------------------------------------------------------------


class TestStatusBadge:
    def test_pass(self) -> None:
        assert _status_badge("pass") == "PASS"

    def test_fail(self) -> None:
        assert _status_badge("fail") == "FAIL"

    def test_warn(self) -> None:
        assert _status_badge("warn") == "WARN"

    def test_unknown(self) -> None:
        assert _status_badge(None) == "N/A"
        assert _status_badge("") == "N/A"


# ---------------------------------------------------------------------------
# Individual metric collectors — when scripts are missing
# ---------------------------------------------------------------------------


class TestQualityGateMetrics:
    def test_returns_unavailable_when_script_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(_gdh, "ROOT", Path("/tmp/nonexistent"))
        result = _collect_quality_gate_metrics()
        assert result.get("available") is False

    def test_has_expected_keys_when_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_proc = mock.MagicMock()
        fake_proc.stdout = "[docs-quality] OK — 0 warnings, 0 blocking violations.\n"
        fake_proc.stderr = ""
        fake_proc.returncode = 0
        with mock.patch("subprocess.run", return_value=fake_proc):
            script_path = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "check_docs_quality.py"
            if not script_path.exists():
                pytest.skip("check_docs_quality.py not on this branch")
            result = _collect_quality_gate_metrics()
        assert "total_blocking" in result
        assert "status" in result


class TestStalenessMetrics:
    def test_returns_unavailable_when_script_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(_gdh, "ROOT", Path("/tmp/nonexistent"))
        result = _collect_stale_docs_metrics()
        assert result.get("available") is False

    def test_parses_json_output(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_json = json.dumps({"total_scanned": 100, "actionable_stale_count": 0, "allowlisted_stale_count": 2})
        fake_proc = mock.MagicMock()
        fake_proc.stdout = fake_json
        fake_proc.returncode = 0
        with mock.patch("subprocess.run", return_value=fake_proc):
            stale_script = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "check_stale_docs.py"
            if not stale_script.exists():
                pytest.skip("check_stale_docs.py not on this branch")
            result = _collect_stale_docs_metrics()
        assert result.get("available") is True
        assert result.get("total_scanned") == 100
        assert result.get("actionable_stale") == 0
        assert result.get("status") == "pass"


class TestFreshnessMetrics:
    def test_returns_unavailable_when_script_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(_gdh, "ROOT", Path("/tmp/nonexistent"))
        result = _collect_freshness_metrics()
        assert result.get("available") is False

    def test_pass_when_exit_zero(self) -> None:
        fake_proc = mock.MagicMock()
        fake_proc.stdout = "OK — all generated docs are fresh.\n"
        fake_proc.returncode = 0
        with mock.patch("subprocess.run", return_value=fake_proc):
            result = _collect_freshness_metrics()
        assert result.get("available") is True
        assert result.get("status") == "pass"

    def test_fail_when_exit_nonzero(self) -> None:
        fake_proc = mock.MagicMock()
        fake_proc.stdout = "Generated docs are stale.\n"
        fake_proc.returncode = 1
        with mock.patch("subprocess.run", return_value=fake_proc):
            result = _collect_freshness_metrics()
        assert result.get("status") == "fail"


class TestAstCatalogMetrics:
    def test_reads_existing_catalog(self) -> None:
        if not _gdh.AST_CATALOG_JSON.exists():
            pytest.skip("AST_RULE_CATALOG.json not present")
        result = _collect_ast_catalog_metrics()
        assert result.get("available") is True
        assert "blocking_gates" in result

    def test_returns_unavailable_when_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(_gdh, "AST_CATALOG_JSON", Path("/tmp/nonexistent.json"))
        result = _collect_ast_catalog_metrics()
        assert result.get("available") is False


class TestAuditMetrics:
    def test_reads_existing_audit_index(self) -> None:
        if not _gdh.AUDIT_INDEX_JSON.exists():
            pytest.skip("MASTER_AUDIT_ISSUE_INDEX.json not present")
        result = _collect_audit_metrics()
        assert result.get("available") is True
        assert "total_issues" in result
        assert "open_issues" in result

    def test_returns_unavailable_when_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(_gdh, "AUDIT_INDEX_JSON", Path("/tmp/nonexistent.json"))
        result = _collect_audit_metrics()
        assert result.get("available") is False


# ---------------------------------------------------------------------------
# collect_all_metrics
# ---------------------------------------------------------------------------


_STUB_METRICS = {
    "quality_gate": {"available": True, "status": "pass", "total_blocking": 0, "total_warnings": 0},
    "stale_docs": {"available": True, "status": "pass", "total_scanned": 5, "actionable_stale": 0},
    "freshness": {"available": True, "status": "pass"},
    "ast_catalog": {"available": False},
    "audit_index": {"available": False},
}


def _patch_collectors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch all subprocess-backed collectors so tests don't shell out."""
    monkeypatch.setattr(_gdh, "_collect_quality_gate_metrics", lambda: _STUB_METRICS["quality_gate"])
    monkeypatch.setattr(_gdh, "_collect_stale_docs_metrics", lambda: _STUB_METRICS["stale_docs"])
    monkeypatch.setattr(_gdh, "_collect_freshness_metrics", lambda: _STUB_METRICS["freshness"])
    monkeypatch.setattr(_gdh, "_collect_ast_catalog_metrics", lambda: _STUB_METRICS["ast_catalog"])
    monkeypatch.setattr(_gdh, "_collect_audit_metrics", lambda: _STUB_METRICS["audit_index"])


class TestCollectAllMetrics:
    def test_has_all_top_level_keys(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_collectors(monkeypatch)
        metrics = collect_all_metrics()
        for key in ("generated_on", "quality_gate", "stale_docs", "freshness", "ast_catalog", "audit_index"):
            assert key in metrics, f"Missing key: {key}"

    def test_generated_on_is_iso_date(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_collectors(monkeypatch)
        metrics = collect_all_metrics()
        assert len(str(metrics["generated_on"])) == 10
        assert str(metrics["generated_on"])[4] == "-"


# ---------------------------------------------------------------------------
# Output files
# ---------------------------------------------------------------------------


class TestOutputFiles:
    def test_json_output_is_valid(self) -> None:
        if not OUTPUT_JSON.exists():
            pytest.skip("DOCS_HEALTH.json not generated yet")
        data = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        assert "generated_on" in data

    def test_markdown_output_exists(self) -> None:
        if not OUTPUT_MD.exists():
            pytest.skip("DOCS_HEALTH.md not generated yet")
        content = OUTPUT_MD.read_text(encoding="utf-8")
        assert "# Docs Health Dashboard" in content
        assert "## Summary" in content

    def test_main_generates_both_outputs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_collectors(monkeypatch)
        monkeypatch.setattr(_gdh, "OUTPUT_JSON", tmp_path / "health.json")
        monkeypatch.setattr(_gdh, "OUTPUT_MD", tmp_path / "health.md")
        exit_code = main([])
        assert exit_code == 0
        assert (tmp_path / "health.json").exists()
        assert (tmp_path / "health.md").exists()
        data = json.loads((tmp_path / "health.json").read_text(encoding="utf-8"))
        assert "generated_on" in data


# ---------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------


class TestInfrastructure:
    def test_ci_workflow_exists(self) -> None:
        wf = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "docs-health-dashboard.yml"
        assert wf.exists(), "docs-health-dashboard.yml CI workflow must exist"

    def test_ci_workflow_has_schedule(self) -> None:
        wf = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "docs-health-dashboard.yml"
        content = wf.read_text(encoding="utf-8")
        assert "schedule" in content and "cron" in content

    def test_makefile_has_health_target(self) -> None:
        makefile = Path(__file__).resolve().parents[2] / "Makefile"
        content = makefile.read_text(encoding="utf-8")
        assert "docs-health-generate" in content

    def test_generate_all_includes_health(self) -> None:
        gen_all = Path(__file__).resolve().parents[2] / "scripts" / "docs" / "generate_all.py"
        content = gen_all.read_text(encoding="utf-8")
        assert "generate_docs_health" in content
