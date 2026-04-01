"""Decision record completeness validation tests.

STORY-270 / EPIC-070: Validates that the formal salvage-vs-rebuild decision
record (ADR-010) cites measured defect rates, failure classes, and scopes the
next backlog wave to proven failure surfaces only.
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Paths to evidence documents
# ---------------------------------------------------------------------------

_DOCS_DIR = Path(__file__).parents[2] / "docs"
_ARCH_DIR = _DOCS_DIR / "architecture"
_AUDIT_DIR = _DOCS_DIR / "audit"

_ADR_010 = _ARCH_DIR / "ADR-010-SALVAGE-DECISION-FROM-GOLDEN-RUN-EVIDENCE.md"
_SALVAGE_DECISION = _ARCH_DIR / "SALVAGE_VS_REBUILD_DECISION.md"
_RUNTIME_LEDGER = _AUDIT_DIR / "RUNTIME_DEPTH_AND_DUPLICATION_LEDGER_2026-03-31.md"
_PROVIDER_SCORECARD = _ARCH_DIR / "provider-scorecard.md"
_DECISIONS = _ARCH_DIR / "decisions.md"


# ---------------------------------------------------------------------------
# ADR-010 existence and structure
# ---------------------------------------------------------------------------


class TestADR010Exists:
    """The formal decision record must exist and be well-formed."""

    def test_adr_010_file_exists(self) -> None:
        """ADR-010 must exist in the architecture docs."""
        assert _ADR_010.exists(), "ADR-010 decision record not found"

    def test_adr_010_has_accepted_status(self) -> None:
        """ADR-010 must have an ACCEPTED status."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "ACCEPTED" in content, "ADR-010 must declare ACCEPTED status"

    def test_adr_010_has_decision_section(self) -> None:
        """ADR-010 must have a Decision section."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "## Decision" in content, "ADR-010 missing Decision section"

    def test_adr_010_has_consequences_section(self) -> None:
        """ADR-010 must have a Consequences section."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "## Consequences" in content, "ADR-010 missing Consequences section"


# ---------------------------------------------------------------------------
# ADR-010 cites measured defect rates
# ---------------------------------------------------------------------------


class TestDecisionCitesMeasuredRates:
    """The decision must cite specific measured defect rates."""

    def test_cites_golden_contract_count(self) -> None:
        """Must cite the number of golden contract tests."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "30" in content, "ADR-010 must cite 30 golden contract tests"

    def test_cites_full_market_count(self) -> None:
        """Must cite the number of full-market regression tests."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "17" in content, "ADR-010 must cite 17 full-market tests"

    def test_cites_placeholder_guard_count(self) -> None:
        """Must cite the number of placeholder guard tests."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "28" in content, "ADR-010 must cite 28 placeholder guard tests"

    def test_cites_total_test_count(self) -> None:
        """Must cite the total golden-run test count."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "88" in content, "ADR-010 must cite 88 total golden-run tests"


# ---------------------------------------------------------------------------
# ADR-010 cites failure classes
# ---------------------------------------------------------------------------


class TestDecisionCitesFailureClasses:
    """The decision must identify and cite resolved failure classes."""

    def test_cites_router_bypass(self) -> None:
        """Must cite the router bypass failure class."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "bypass" in content.lower(), "ADR-010 must cite router bypass failure"

    def test_cites_placeholder_nodes(self) -> None:
        """Must cite placeholder graph nodes as a failure class."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "placeholder" in content.lower(), "ADR-010 must cite placeholder nodes"

    def test_cites_duplicate_adapters(self) -> None:
        """Must cite duplicate adapter pairs as a failure class."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "duplicate" in content.lower(), "ADR-010 must cite duplicate adapters"


# ---------------------------------------------------------------------------
# ADR-010 scopes next backlog wave
# ---------------------------------------------------------------------------


class TestNextBacklogWaveScoped:
    """The next backlog wave must be scoped to proven failure surfaces."""

    def test_has_next_backlog_section(self) -> None:
        """ADR-010 must define the next backlog wave."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "Next Backlog Wave" in content, "ADR-010 missing next backlog wave"

    def test_scopes_placeholder_elimination(self) -> None:
        """Next wave must target placeholder elimination."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "Placeholder" in content, "Next wave must target placeholder elimination"

    def test_scopes_graph_deletion(self) -> None:
        """Next wave must target graph runtime deletion."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "Graph Runtime Deletion" in content or "delete graph" in content.lower(), (
            "Next wave must scope graph runtime deletion"
        )


# ---------------------------------------------------------------------------
# Evidence documents referenced
# ---------------------------------------------------------------------------


class TestEvidenceDocumentsExist:
    """All evidence documents cited by ADR-010 must exist."""

    def test_salvage_decision_exists(self) -> None:
        """SALVAGE_VS_REBUILD_DECISION.md must exist."""
        assert _SALVAGE_DECISION.exists(), "SALVAGE_VS_REBUILD_DECISION.md not found"

    def test_runtime_ledger_exists(self) -> None:
        """Runtime depth ledger must exist."""
        assert _RUNTIME_LEDGER.exists(), "Runtime depth ledger not found"

    def test_provider_scorecard_exists(self) -> None:
        """Provider scorecard must exist."""
        assert _PROVIDER_SCORECARD.exists(), "Provider scorecard not found"

    def test_decisions_file_exists(self) -> None:
        """Architecture decisions file must exist."""
        assert _DECISIONS.exists(), "Architecture decisions file not found"

    def test_golden_runs_package_exists(self) -> None:
        """Golden runs test package must exist."""
        golden_dir = Path(__file__).parent
        assert (golden_dir / "__init__.py").exists(), "golden_runs package missing"

    @pytest.mark.parametrize(
        "artifact",
        [
            "yahoo_finance_success.json",
            "yahoo_finance_degraded.json",
            "patents_success.json",
            "patents_degraded.json",
        ],
    )
    def test_golden_contract_artifacts_exist(self, artifact: str) -> None:
        """Golden contract artifact files must exist."""
        artifacts_dir = Path(__file__).parent / "artifacts"
        assert (artifacts_dir / artifact).exists(), f"Missing artifact: {artifact}"


# ---------------------------------------------------------------------------
# ADR-010 references all evidence sources
# ---------------------------------------------------------------------------


class TestADR010ReferencesEvidence:
    """ADR-010 must reference all evidence sources by story number."""

    @pytest.mark.parametrize(
        "story_ref",
        [
            "STORY-271",
            "STORY-263",
            "STORY-267",
            "STORY-268",
            "STORY-269",
            "STORY-258",
        ],
    )
    def test_references_story(self, story_ref: str) -> None:
        """ADR-010 must reference each evidence-producing story."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert story_ref in content, f"ADR-010 must reference {story_ref}"

    def test_references_adr_009(self) -> None:
        """ADR-010 must reference the graph freeze ADR-009."""
        content = _ADR_010.read_text(encoding="utf-8")
        assert "ADR-009" in content, "ADR-010 must reference ADR-009 graph freeze"
