from __future__ import annotations

from typing import Protocol

import pytest

from solstein.data.unified import enrichment as enrichment_module
from solstein.data.unified.batch_outcomes import BatchEnrichmentOutcome
from solstein.data.unified.company import UnifiedCompany


class _DummyCache:
    def get(self, key: str) -> dict[str, object] | None:
        return None

    def set(self, key: str, value: dict[str, object]) -> None:
        return None


class _DummyMetrics:
    def __init__(self) -> None:
        self.successful = 0
        self.failed = 0

    def record_enrichment(self, duration_ms: int, success: bool) -> None:
        if success:
            self.successful += 1
        else:
            self.failed += 1

    def get_summary(self) -> dict[str, float | int]:
        total = self.successful + self.failed
        return {
            "successful": self.successful,
            "failed": self.failed,
            "avg_duration_ms": 0.0,
            "total": total,
        }


class _LoaderLike(Protocol):
    cache: _DummyCache
    metrics: _DummyMetrics


class _DummyLoader:
    def __init__(self) -> None:
        self.cache = _DummyCache()
        self.metrics = _DummyMetrics()


def _make_loader() -> _DummyLoader:
    return _DummyLoader()


def test_enrich_batch_returns_explicit_failure_outcome_on_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    loader = _make_loader()
    companies = [
        UnifiedCompany(id="ok1", name="OK Corp"),
        UnifiedCompany(id="bad", name="Bad Corp"),
    ]

    def fake_enrich_from_connectors(loader_arg: _LoaderLike, company: UnifiedCompany) -> UnifiedCompany:
        if company.id == "bad":
            raise RuntimeError("connector timeout")
        enriched = company.model_copy(deep=True)
        enriched.enrichment_sources.append("sec_edgar")
        return enriched

    monkeypatch.setattr(enrichment_module, "enrich_from_connectors", fake_enrich_from_connectors)

    outcomes = enrichment_module.enrich_batch(loader, companies, batch_size=10)

    assert all(isinstance(outcome, BatchEnrichmentOutcome) for outcome in outcomes)
    assert [outcome.status for outcome in outcomes] == ["success", "failure"]
    assert outcomes[1].company.id == "bad"
    assert outcomes[1].company is not companies[1]
    assert outcomes[1].company.enrichment_errors == ["[batch_enrichment] connector timeout"]
    assert loader.metrics.failed == 1


def test_enrich_batch_marks_enrichment_errors_as_partial(monkeypatch: pytest.MonkeyPatch) -> None:
    loader = _make_loader()
    company = UnifiedCompany(id="partial", name="Partial Corp")

    def fake_enrich_from_connectors(loader_arg: _LoaderLike, input_company: UnifiedCompany) -> UnifiedCompany:
        enriched = input_company.model_copy(deep=True)
        enriched.enrichment_errors.append("[SEC_EDGAR] degraded response")
        return enriched

    monkeypatch.setattr(enrichment_module, "enrich_from_connectors", fake_enrich_from_connectors)

    outcomes = enrichment_module.enrich_batch(loader, [company], batch_size=10)

    assert len(outcomes) == 1
    assert outcomes[0].status == "partial"
    assert outcomes[0].errors == ["[SEC_EDGAR] degraded response"]
    assert outcomes[0].company.id == "partial"
