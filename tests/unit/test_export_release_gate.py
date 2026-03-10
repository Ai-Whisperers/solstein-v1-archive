from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from dataclasses import dataclass
from typing import TypeVar

import pytest
from _pytest.monkeypatch import MonkeyPatch

from solstein.api.exceptions import APIError
from solstein.api.routers import export as export_router
from solstein.data.report_release_gate import GateReason, ReportGateResult
from solstein.domain.models import Company, FinancialMetric


@dataclass
class _DummyRepo:
    companies: list[Company]

    async def get_all_filtered(self, industry: str | None, skip: int, limit: int) -> list[Company]:
        _ = (industry, skip, limit)
        return self.companies

    def get_all(self, filters: object | None = None) -> list[Company]:
        _ = filters
        return self.companies


def _company(name: str, data_source_type: str = "synthetic") -> Company:
    return Company(
        id=name.lower().replace(" ", "-"),
        name=name,
        industry="Energy",
        data_source_type=data_source_type,
        financials=FinancialMetric(
            revenue=10.0,
            employees=20,
            growth_rate=12.0,
            profit_margin=6.0,
            valuation=55.0,
        ),
        confidence_scores={
            "revenue_confidence": 0.9,
            "employees_confidence": 0.9,
            "growth_rate_confidence": 0.9,
            "profit_margin_confidence": 0.9,
            "funding_raised_confidence": 0.9,
            "valuation_confidence": 0.9,
        },
    )


T = TypeVar("T")


def _run(coro: Coroutine[object, object, T]) -> T:
    return asyncio.run(coro)


def _identity(company: Company) -> Company:
    return company


def test_export_to_json_blocks_on_release_gate(monkeypatch: MonkeyPatch) -> None:
    companies = [_company("Synthetic Co")]
    repo = _DummyRepo(companies=companies)

    class _GateStub:
        def evaluate(self, _companies: list[Company]) -> ReportGateResult:
            return ReportGateResult(
                passed=False,
                reasons=[GateReason(code="gap_analysis", message="blocked", details={})],
            )

    def _fake_gate(*_args: object, **_kwargs: object) -> _GateStub:
        return _GateStub()

    monkeypatch.setattr(export_router, "ReportReleaseGate", _fake_gate)

    monkeypatch.setattr(export_router.growth_scorer, "calculate_scores", _identity)

    with pytest.raises(APIError) as exc_info:
        _ = _run(export_router.export_to_json(industry=None, _={}, repo=repo))

    assert exc_info.value.code == "RELEASE_GATE_BLOCKED"


def test_excel_export_skips_when_gate_blocks(monkeypatch: MonkeyPatch) -> None:
    companies = [_company("Synthetic Co")]
    repo = _DummyRepo(companies=companies)

    created_paths: list[str] = []

    class _GateStub:
        def evaluate(self, _companies: list[Company]) -> ReportGateResult:
            return ReportGateResult(
                passed=False,
                reasons=[GateReason(code="gap_analysis", message="blocked", details={})],
            )

    def _fake_gate(*_args: object, **_kwargs: object) -> _GateStub:
        return _GateStub()

    monkeypatch.setattr(export_router, "ReportReleaseGate", _fake_gate)
    scoring_calls = {"count": 0}

    def _counted_identity(company: Company) -> Company:
        scoring_calls["count"] += 1
        return company

    monkeypatch.setattr(export_router.growth_scorer, "calculate_scores", _counted_identity)

    def _fake_create_dashboard(_companies: object, output_path: object) -> None:
        created_paths.append(str(output_path))

    monkeypatch.setattr(export_router.excel_exporter, "create_dashboard", _fake_create_dashboard)

    export_router._run_excel_export(repo, filters={}, filename="test.xlsx")

    assert created_paths == []
    assert scoring_calls["count"] == 0
