import asyncio
from collections.abc import Coroutine
from types import SimpleNamespace
from typing import Any

import pytest
from _pytest.monkeypatch import MonkeyPatch

from solstein.api.routers import scoring
from solstein.data.report_release_gate import GateReason, ReportGateResult


class _DummyRepo:
    async def get_by_id(self, _company_id: str):
        return None

    async def save(self, _company):
        return None


def _run(coro: Coroutine[Any, Any, dict[str, Any]]) -> dict[str, Any]:
    return asyncio.get_event_loop().run_until_complete(coro)


def test_shadow_mode_defaults_to_legacy_when_flag_disabled(monkeypatch: MonkeyPatch) -> None:
    target_company = SimpleNamespace(id="c1")
    scored_company = SimpleNamespace(
        growth_score=8.5,
        financial_health_score=5.0,
        competitive_position_score=6.0,
        composite_score=2.0,
        classification="Lead",
        scoring_breakdown={"x": 1},
    )

    monkeypatch.setattr(scoring.unified_score_loader, "load_company_for_scoring", lambda _cid: target_company)

    class _GatePass:
        def evaluate(self, _companies):
            return ReportGateResult(passed=True, reasons=[])

    monkeypatch.setattr(scoring, "ReportReleaseGate", lambda *args, **kwargs: _GatePass())
    monkeypatch.setattr(scoring.growth_scorer, "calculate_scores", lambda _company: scored_company)
    monkeypatch.setattr(scoring, "get_settings", lambda: SimpleNamespace(feature_new_classifier=False))

    result = _run(scoring.score_company("c1", _={}, repo=_DummyRepo()))

    assert result["classification"] == "Phoenix"  # legacy based on growth
    assert result["classification_shadow"]["legacy"] == "Phoenix"
    assert result["classification_shadow"]["canonical"] == "Lead"
    assert result["classification_shadow"]["mismatch"] is True
    assert result["classification_shadow"]["feature_new_classifier"] is False


def test_shadow_mode_switches_to_canonical_when_flag_enabled(monkeypatch: MonkeyPatch) -> None:
    target_company = SimpleNamespace(id="c2")
    scored_company = SimpleNamespace(
        growth_score=2.0,
        financial_health_score=4.0,
        competitive_position_score=5.0,
        composite_score=8.1,
        classification="Phoenix",
        scoring_breakdown={"x": 1},
    )

    monkeypatch.setattr(scoring.unified_score_loader, "load_company_for_scoring", lambda _cid: target_company)

    class _GatePass:
        def evaluate(self, _companies):
            return ReportGateResult(passed=True, reasons=[])

    monkeypatch.setattr(scoring, "ReportReleaseGate", lambda *args, **kwargs: _GatePass())
    monkeypatch.setattr(scoring.growth_scorer, "calculate_scores", lambda _company: scored_company)
    monkeypatch.setattr(scoring, "get_settings", lambda: SimpleNamespace(feature_new_classifier=True))

    result = _run(scoring.score_company("c2", _={}, repo=_DummyRepo()))

    assert result["classification"] == "Phoenix"  # canonical selected by feature flag
    assert result["classification_shadow"]["legacy"] == "Lead"
    assert result["classification_shadow"]["canonical"] == "Phoenix"
    assert result["classification_shadow"]["mismatch"] is True
    assert result["classification_shadow"]["feature_new_classifier"] is True


def test_score_company_blocks_when_release_gate_fails(monkeypatch: MonkeyPatch) -> None:
    target_company = SimpleNamespace(id="c3")
    monkeypatch.setattr(scoring.unified_score_loader, "load_company_for_scoring", lambda _cid: target_company)

    class _GateFail:
        def evaluate(self, _companies):
            return ReportGateResult(
                passed=False,
                reasons=[GateReason(code="critical_claim_contradiction", message="blocked", details={})],
            )

    monkeypatch.setattr(scoring, "ReportReleaseGate", lambda *args, **kwargs: _GateFail())

    with pytest.raises(scoring.APIError) as exc_info:
        _ = _run(scoring.score_company("c3", _={}, repo=_DummyRepo()))

    assert exc_info.value.code == "RELEASE_GATE_BLOCKED"
