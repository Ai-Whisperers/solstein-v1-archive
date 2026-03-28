"""Tests for scripts/ci/check_stale_docs.py (STORY-239).

Covers:
- Staleness class resolution (most-specific prefix wins)
- Ownership resolution (most-specific prefix wins)
- Allowlist mechanism (file-exact and file_prefix)
- Age calculation
- CLI exit codes (--fail flag)
- Policy and allowlist schema validation
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_SCRIPTS_CI = Path(__file__).resolve().parents[2] / "scripts" / "ci"
if str(_SCRIPTS_CI) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_CI))

import check_stale_docs as _csd
from check_stale_docs import (
    DocClassPolicy,
    StaleDoc,
    StalenessReport,
    _is_allowlisted,
    _resolve_class,
    _resolve_owner,
    main,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_policy(prefix: str, max_age: int, class_id: str = "test") -> DocClassPolicy:
    return DocClassPolicy(
        class_id=class_id,
        description="test",
        path_prefixes=[prefix],
        max_age_days=max_age,
        owner_team="test-team",
        escalation_owner="platform-team",
    )


def _make_stale(file: str = "docs/x.md", age: int = 100, owner: str = "docs-team") -> StaleDoc:
    return StaleDoc(
        file=file,
        last_modified="2025-01-01",
        age_days=age,
        max_age_days=90,
        class_id="governance",
        owner_team=owner,
    )


# ---------------------------------------------------------------------------
# Class resolution tests
# ---------------------------------------------------------------------------


class TestResolveClass:
    def test_returns_none_when_no_classes(self) -> None:
        assert _resolve_class("docs/foo.md", []) is None

    def test_matches_exact_prefix(self) -> None:
        cls = _make_policy("docs/governance/", 90, "governance")
        result = _resolve_class("docs/governance/policy.md", [cls])
        assert result is not None
        assert result.class_id == "governance"

    def test_most_specific_prefix_wins(self) -> None:
        broad = _make_policy("docs/", 365, "default")
        specific = _make_policy("docs/governance/", 90, "governance")
        result = _resolve_class("docs/governance/policy.md", [broad, specific])
        assert result is not None
        assert result.class_id == "governance"

    def test_no_match_returns_none(self) -> None:
        cls = _make_policy("docs/governance/", 90)
        result = _resolve_class("backlog/epic.md", [cls])
        assert result is None

    def test_multiple_prefixes_on_one_class(self) -> None:
        cls = DocClassPolicy(
            class_id="dual",
            description="dual prefix",
            path_prefixes=["docs/audit/", "docs/governance/"],
            max_age_days=90,
            owner_team="team",
            escalation_owner="platform-team",
        )
        assert _resolve_class("docs/audit/report.md", [cls]) is not None
        assert _resolve_class("docs/governance/policy.md", [cls]) is not None
        assert _resolve_class("docs/other/file.md", [cls]) is None


# ---------------------------------------------------------------------------
# Ownership resolution tests
# ---------------------------------------------------------------------------


class TestResolveOwner:
    def test_default_returns_unowned_owner(self) -> None:
        owner = _resolve_owner("docs/unknown/file.md", {}, "platform-team")
        assert owner == "platform-team"

    def test_most_specific_prefix_wins(self) -> None:
        mapping = {
            "docs/": "docs-team",
            "docs/reference/": "backend-team",
        }
        owner = _resolve_owner("docs/reference/api.md", mapping, "platform-team")
        assert owner == "backend-team"

    def test_broad_prefix_used_when_specific_not_matched(self) -> None:
        mapping = {
            "docs/": "docs-team",
            "docs/reference/": "backend-team",
        }
        owner = _resolve_owner("docs/guides/intro.md", mapping, "platform-team")
        assert owner == "docs-team"


# ---------------------------------------------------------------------------
# Allowlist tests
# ---------------------------------------------------------------------------


class TestAllowlist:
    def test_exact_file_match(self) -> None:
        allowlist = [
            {"owner": "t", "rationale": "r", "expiry": "2099", "file": "docs/foo.md"}
        ]
        allowed, rationale = _is_allowlisted("docs/foo.md", allowlist)
        assert allowed is True
        assert rationale == "r"

    def test_file_prefix_match(self) -> None:
        allowlist = [
            {"owner": "t", "rationale": "prefix-reason", "expiry": "2099", "file_prefix": "docs/agent-cycles/"}
        ]
        allowed, reason = _is_allowlisted("docs/agent-cycles/2026/cycle.md", allowlist)
        assert allowed is True
        assert reason == "prefix-reason"

    def test_no_match(self) -> None:
        allowlist = [
            {"owner": "t", "rationale": "r", "expiry": "2099", "file": "docs/other.md"}
        ]
        allowed, _ = _is_allowlisted("docs/foo.md", allowlist)
        assert allowed is False

    def test_empty_allowlist(self) -> None:
        allowed, _ = _is_allowlisted("docs/anything.md", [])
        assert allowed is False


# ---------------------------------------------------------------------------
# StalenessReport property tests
# ---------------------------------------------------------------------------


class TestStalenessReport:
    def test_actionable_excludes_allowlisted(self) -> None:
        report = StalenessReport(generated_on="2026-01-01", search_root="docs")
        report.stale.append(_make_stale("docs/a.md"))
        report.stale.append(StaleDoc("docs/b.md", "2025-01-01", 100, 90, "g", "t", allowlisted=True))
        assert len(report.actionable) == 1
        assert report.actionable[0].file == "docs/a.md"

    def test_allowlisted_property(self) -> None:
        report = StalenessReport(generated_on="2026-01-01", search_root="docs")
        report.stale.append(_make_stale("docs/a.md"))
        report.stale.append(StaleDoc("docs/b.md", "2025-01-01", 100, 90, "g", "t", allowlisted=True))
        assert len(report.allowlisted) == 1
        assert report.allowlisted[0].file == "docs/b.md"


# ---------------------------------------------------------------------------
# CLI exit code tests
# ---------------------------------------------------------------------------


class TestCLI:
    def test_exit_zero_without_fail_flag_even_with_stale(self, monkeypatch: pytest.MonkeyPatch) -> None:
        report = StalenessReport(generated_on="2026-01-01", search_root="docs")
        report.stale.append(_make_stale("docs/stale.md"))
        report.total_scanned = 1
        monkeypatch.setattr(_csd, "run_scan", lambda _: report)
        exit_code = main(["--path", "docs"])
        assert exit_code == 0

    def test_exit_one_with_fail_flag_and_stale_docs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        report = StalenessReport(generated_on="2026-01-01", search_root="docs")
        report.stale.append(_make_stale("docs/stale.md"))
        report.total_scanned = 1
        monkeypatch.setattr(_csd, "run_scan", lambda _: report)
        exit_code = main(["--path", "docs", "--fail"])
        assert exit_code == 1

    def test_exit_zero_with_fail_flag_and_clean_docs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        report = StalenessReport(generated_on="2026-01-01", search_root="docs")
        report.total_scanned = 10
        monkeypatch.setattr(_csd, "run_scan", lambda _: report)
        exit_code = main(["--path", "docs", "--fail"])
        assert exit_code == 0

    def test_exit_one_for_nonexistent_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(_csd, "ROOT", Path("/tmp"))
        exit_code = main(["--path", "nonexistent-dir-xyz"])
        assert exit_code == 1

    def test_json_output_is_valid(self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
        report = StalenessReport(generated_on="2026-01-01", search_root="docs")
        report.total_scanned = 5
        monkeypatch.setattr(_csd, "run_scan", lambda _: report)
        exit_code = main(["--path", "docs", "--json"])
        assert exit_code == 0
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert "actionable_stale_count" in parsed
        assert "total_scanned" in parsed
        assert parsed["total_scanned"] == 5


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


class TestPolicySchema:
    def test_policy_file_exists(self) -> None:
        assert (Path(__file__).resolve().parents[2] / "scripts" / "ci" / "stale-docs-policy.json").exists()

    def test_policy_has_required_fields(self) -> None:
        policy_path = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "stale-docs-policy.json"
        raw = json.loads(policy_path.read_text(encoding="utf-8"))
        assert "classes" in raw
        assert "ownership_map" in raw
        for cls in raw["classes"]:
            for field in ("class_id", "description", "path_prefixes", "max_age_days", "owner_team"):
                assert field in cls, f"Class missing field '{field}': {cls}"

    def test_allowlist_file_exists(self) -> None:
        assert (Path(__file__).resolve().parents[2] / "scripts" / "ci" / "stale-docs-allowlist.json").exists()

    def test_allowlist_entries_have_required_fields(self) -> None:
        allowlist_path = Path(__file__).resolve().parents[2] / "scripts" / "ci" / "stale-docs-allowlist.json"
        entries = json.loads(allowlist_path.read_text(encoding="utf-8"))
        for entry in entries:
            assert "owner" in entry, f"Entry missing 'owner': {entry}"
            assert "rationale" in entry, f"Entry missing 'rationale': {entry}"
            assert "expiry" in entry, f"Entry missing 'expiry': {entry}"
            assert "file" in entry or "file_prefix" in entry, f"Entry missing 'file' or 'file_prefix': {entry}"

    def test_ci_workflow_exists(self) -> None:
        workflow = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "stale-docs.yml"
        assert workflow.exists(), "stale-docs.yml CI workflow must exist"

    def test_makefile_has_stale_check_target(self) -> None:
        makefile = Path(__file__).resolve().parents[2] / "Makefile"
        content = makefile.read_text(encoding="utf-8")
        assert "docs-stale-check" in content

    def test_script_runs_without_error(self) -> None:
        """Integration test: ensure the detector runs on the actual repo without crashing."""
        result = subprocess.run(
            ["python3", "scripts/ci/check_stale_docs.py", "--path", "docs", "--json"],
            cwd=str(Path(__file__).resolve().parents[2]),
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"
        parsed = json.loads(result.stdout)
        assert "total_scanned" in parsed
        assert parsed["total_scanned"] > 0
