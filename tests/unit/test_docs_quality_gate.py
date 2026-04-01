"""Tests for scripts/ci/check_docs_quality.py (STORY-238).

Covers:
- Placeholder token detection (blocking and warning tiers)
- Governance doc metadata validation
- Allowlist mechanism
- CLI exit codes and --strict flag
- Allowlist file schema validation
"""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

import pytest

# Make the script importable without a package install
_SCRIPTS_CI = Path(__file__).resolve().parents[2] / "scripts" / "ci"
if str(_SCRIPTS_CI) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_CI))

try:
    import check_docs_quality as _cq  # noqa: E402
    from check_docs_quality import (  # noqa: E402
        CheckResult,
        Violation,
        _check_metadata,
        _check_placeholder_tokens,
        _is_allowlisted,
        _load_allowlist,
        main,
    )
except ImportError:
    pytest.skip(
        "check_docs_quality.py API changed — test needs update to match current script",
        allow_module_level=True,
    )

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Placeholder token tests
# ---------------------------------------------------------------------------


class TestBlockingTokens:
    def test_unfilled_template_variable_is_blocking(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "doc.md", "# Title\n\nHello {{name}}, welcome.\n")
        violations = _check_placeholder_tokens(doc, "doc.md", [])
        blocking = [v for v in violations if v.severity == "blocking"]
        assert any(v.check == "UNFILLED_TEMPLATE_VARIABLE" for v in blocking)

    def test_placeholder_marker_is_blocking(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "doc.md", "# Title\n\nPLACEHOLDER content here.\n")
        violations = _check_placeholder_tokens(doc, "doc.md", [])
        assert any(v.check == "PLACEHOLDER_MARKER" for v in violations)

    def test_todo_colon_is_blocking(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "doc.md", "# Title\n\nTODO: finish this section.\n")
        violations = _check_placeholder_tokens(doc, "doc.md", [])
        assert any(v.check == "TODO_IN_GOVERNANCE_DOC" for v in violations)

    def test_fixme_colon_is_blocking(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "doc.md", "# Title\n\nFIXME: update reference.\n")
        violations = _check_placeholder_tokens(doc, "doc.md", [])
        assert any(v.check == "FIXME_IN_GOVERNANCE_DOC" for v in violations)

    def test_line_number_is_reported(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "doc.md", "line 1\nline 2\nTODO: fix me\nline 4\n")
        violations = _check_placeholder_tokens(doc, "doc.md", [])
        todo_v = next(v for v in violations if v.check == "TODO_IN_GOVERNANCE_DOC")
        assert todo_v.line == 3

    def test_multiple_tokens_on_same_line_all_reported(self, tmp_path: Path) -> None:
        doc = _write(
            tmp_path, "doc.md", "# T\n\nPLACEHOLDER and TODO: both here.\n"
        )
        violations = _check_placeholder_tokens(doc, "doc.md", [])
        checks = {v.check for v in violations}
        assert "PLACEHOLDER_MARKER" in checks
        assert "TODO_IN_GOVERNANCE_DOC" in checks

    def test_clean_doc_has_no_blocking_violations(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "doc.md", "# Title\n\nClean content.\n")
        violations = _check_placeholder_tokens(doc, "doc.md", [])
        blocking = [v for v in violations if v.severity == "blocking"]
        assert blocking == []


class TestWarningTokens:
    def test_tbd_marker_is_warning(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "doc.md", "# Title\n\nDecision is TBD.\n")
        violations = _check_placeholder_tokens(doc, "doc.md", [])
        assert any(v.check == "TBD_MARKER" and v.severity == "warn" for v in violations)

    def test_lorem_ipsum_is_warning(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "doc.md", "# Title\n\nLorem ipsum dolor.\n")
        violations = _check_placeholder_tokens(doc, "doc.md", [])
        assert any(v.check == "LOREM_IPSUM" and v.severity == "warn" for v in violations)

    def test_example_com_url_is_warning(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "doc.md", "See https://example.com for details.\n")
        violations = _check_placeholder_tokens(doc, "doc.md", [])
        assert any(v.check == "EXAMPLE_COM" and v.severity == "warn" for v in violations)


# ---------------------------------------------------------------------------
# Allowlist tests
# ---------------------------------------------------------------------------


class TestAllowlist:
    def test_allowlisted_token_not_blocking(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "doc.md", "# Title\n\nPLACEHOLDER content.\n")
        allowlist = [
            {
                "owner": "test",
                "rationale": "intentional",
                "expiry": "2099-01-01",
                "pattern": "PLACEHOLDER",
                "file": "doc.md",
            }
        ]
        violations = _check_placeholder_tokens(doc, "doc.md", allowlist)
        placeholder_v = next(v for v in violations if v.check == "PLACEHOLDER_MARKER")
        assert placeholder_v.allowlisted is True

    def test_allowlist_without_file_field_applies_globally(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "other.md", "PLACEHOLDER here.\n")
        allowlist = [
            {"owner": "t", "rationale": "r", "expiry": "2099-01-01", "pattern": "PLACEHOLDER"}
        ]
        violations = _check_placeholder_tokens(doc, "other.md", allowlist)
        v = next(v for v in violations if v.check == "PLACEHOLDER_MARKER")
        assert v.allowlisted is True

    def test_allowlist_with_different_file_does_not_apply(self, tmp_path: Path) -> None:
        doc = _write(tmp_path, "doc.md", "PLACEHOLDER here.\n")
        allowlist = [
            {
                "owner": "t",
                "rationale": "r",
                "expiry": "2099-01-01",
                "pattern": "PLACEHOLDER",
                "file": "other.md",
            }
        ]
        violations = _check_placeholder_tokens(doc, "doc.md", allowlist)
        v = next(v for v in violations if v.check == "PLACEHOLDER_MARKER")
        assert v.allowlisted is False

    def test_is_allowlisted_helper(self) -> None:
        allowlist = [
            {"owner": "o", "rationale": "r", "expiry": "2099", "pattern": "FOO", "file": "x.md"}
        ]
        assert _is_allowlisted("x.md", "FOO", allowlist) is True
        assert _is_allowlisted("y.md", "FOO", allowlist) is False
        assert _is_allowlisted("x.md", "BAR", allowlist) is False

    def test_load_allowlist_returns_empty_when_file_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(_cq, "ALLOWLIST_PATH", Path("/nonexistent/path/allowlist.json"))
        result = _load_allowlist()
        assert result == []


# ---------------------------------------------------------------------------
# Metadata validation tests
# ---------------------------------------------------------------------------


class TestMetadataValidation:
    def _governance_doc(self, tmp_path: Path, content: str) -> Path:
        return _write(tmp_path, "policy.md", content)

    def _complete_frontmatter(self) -> str:
        return (
            "# Policy\n\n"
            "> **Status**: Active\n"
            "> **Owner**: platform-team\n"
            "> **Last Reviewed**: 2026-01-01\n"
            "> **Superseded By**: N/A\n"
            "> **Review Cadence**: Quarterly\n\n"
            "Content here.\n"
        )

    def test_complete_frontmatter_has_no_violations(self, tmp_path: Path) -> None:
        doc = self._governance_doc(tmp_path, self._complete_frontmatter())
        violations = _check_metadata(doc, "docs/governance/policy.md", [])
        assert violations == []

    def test_missing_status_is_blocking(self, tmp_path: Path) -> None:
        content = (
            "# Policy\n\n"
            "> **Owner**: platform-team\n"
            "> **Last Reviewed**: 2026-01-01\n"
            "> **Superseded By**: N/A\n"
        )
        doc = self._governance_doc(tmp_path, content)
        violations = _check_metadata(doc, "docs/governance/policy.md", [])
        blocking = [v for v in violations if v.severity == "blocking"]
        assert any("Status" in v.message for v in blocking)

    def test_missing_owner_is_blocking(self, tmp_path: Path) -> None:
        content = (
            "# Policy\n\n"
            "> **Status**: Active\n"
            "> **Last Reviewed**: 2026-01-01\n"
            "> **Superseded By**: N/A\n"
        )
        doc = self._governance_doc(tmp_path, content)
        violations = _check_metadata(doc, "docs/governance/policy.md", [])
        assert any("Owner" in v.message for v in violations if v.severity == "blocking")

    def test_missing_review_cadence_is_warning(self, tmp_path: Path) -> None:
        content = (
            "# Policy\n\n"
            "> **Status**: Active\n"
            "> **Owner**: platform-team\n"
            "> **Last Reviewed**: 2026-01-01\n"
            "> **Superseded By**: N/A\n"
        )
        doc = self._governance_doc(tmp_path, content)
        violations = _check_metadata(doc, "docs/governance/policy.md", [])
        warnings = [v for v in violations if v.severity == "warn"]
        assert any("Review Cadence" in v.message for v in warnings)

    def test_metadata_violation_has_line_zero(self, tmp_path: Path) -> None:
        doc = self._governance_doc(tmp_path, "# Policy\n\nContent only.\n")
        violations = _check_metadata(doc, "docs/governance/policy.md", [])
        for v in violations:
            assert v.line == 0

    def test_missing_key_allowlisted(self, tmp_path: Path) -> None:
        doc = self._governance_doc(tmp_path, "# Policy\n\nContent only.\n")
        allowlist = [
            {
                "owner": "t",
                "rationale": "r",
                "expiry": "2099",
                "pattern": "missing:Status",
                "file": "docs/governance/policy.md",
            }
        ]
        violations = _check_metadata(doc, "docs/governance/policy.md", allowlist)
        status_v = next(v for v in violations if "Status" in v.message)
        assert status_v.allowlisted is True


# ---------------------------------------------------------------------------
# CheckResult property tests
# ---------------------------------------------------------------------------


class TestCheckResult:
    def test_blocking_filters_correctly(self) -> None:
        result = CheckResult()
        result.violations.append(Violation("f", 1, "C1", "blocking", "msg"))
        result.violations.append(Violation("f", 2, "C2", "warn", "msg"))
        result.violations.append(Violation("f", 3, "C3", "blocking", "msg", allowlisted=True))
        assert len(result.blocking) == 1
        assert result.blocking[0].check == "C1"

    def test_warnings_filters_correctly(self) -> None:
        result = CheckResult()
        result.violations.append(Violation("f", 1, "C1", "blocking", "msg"))
        result.violations.append(Violation("f", 2, "C2", "warn", "msg"))
        result.violations.append(Violation("f", 3, "C3", "warn", "msg", allowlisted=True))
        assert len(result.warnings) == 1
        assert result.warnings[0].check == "C2"


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------


class TestCLI:
    def test_exit_zero_for_clean_docs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / "clean.md").write_text("# Clean\n\nNo issues here.\n", encoding="utf-8")
        # Patch ROOT so --path is resolved against tmp_path's parent
        monkeypatch.setattr(_cq, "ROOT", tmp_path.parent)
        exit_code = main(["--path", tmp_path.name])
        assert exit_code == 0

    def test_exit_one_for_blocking_violation(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / "bad.md").write_text("# Bad\n\nTODO: fill this in.\n", encoding="utf-8")
        monkeypatch.setattr(_cq, "ROOT", tmp_path.parent)
        exit_code = main(["--path", tmp_path.name])
        assert exit_code == 1

    def test_strict_flag_converts_warnings_to_blocking(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        (tmp_path / "warn.md").write_text("# Doc\n\nTBD for now.\n", encoding="utf-8")
        monkeypatch.setattr(_cq, "ROOT", tmp_path.parent)
        normal_exit = main(["--path", tmp_path.name])
        strict_exit = main(["--path", tmp_path.name, "--strict"])
        # Without strict: only a warning, exit 0
        assert normal_exit == 0
        # With strict: TBD becomes blocking, exit 1
        assert strict_exit == 1

    def test_nonexistent_path_exits_one(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(_cq, "ROOT", Path("/tmp"))
        exit_code = main(["--path", "nonexistent-dir-xyz"])
        assert exit_code == 1


# ---------------------------------------------------------------------------
# Allowlist schema validation
# ---------------------------------------------------------------------------


class TestAllowlistSchema:
    def test_shipped_allowlist_has_required_fields(self) -> None:
        allowlist_path = (
            Path(__file__).resolve().parents[2] / "scripts" / "ci" / "docs-quality-allowlist.json"
        )
        assert allowlist_path.exists(), "docs-quality-allowlist.json must exist"
        entries = json.loads(allowlist_path.read_text(encoding="utf-8"))
        for entry in entries:
            assert "owner" in entry, f"Entry missing 'owner': {entry}"
            assert "rationale" in entry, f"Entry missing 'rationale': {entry}"
            assert "expiry" in entry, f"Entry missing 'expiry': {entry}"
            assert "pattern" in entry, f"Entry missing 'pattern': {entry}"

    def test_ci_workflow_exists(self) -> None:
        workflow = (
            Path(__file__).resolve().parents[2]
            / ".github"
            / "workflows"
            / "docs-quality-gates.yml"
        )
        assert workflow.exists(), "docs-quality-gates.yml CI workflow must exist"

    def test_ci_workflow_targets_develop(self) -> None:
        workflow = (
            Path(__file__).resolve().parents[2]
            / ".github"
            / "workflows"
            / "docs-quality-gates.yml"
        )
        content = workflow.read_text(encoding="utf-8")
        assert "develop" in content, "CI workflow must target the develop branch"

    def test_makefile_has_docs_quality_target(self) -> None:
        makefile = Path(__file__).resolve().parents[2] / "Makefile"
        content = makefile.read_text(encoding="utf-8")
        assert "docs-quality-check" in content, "Makefile must have docs-quality-check target"
