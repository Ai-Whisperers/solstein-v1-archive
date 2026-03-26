"""Regression tests for connector fact schema boundary validation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from solstein.infrastructure.refresh import BaseRefreshConnector
from solstein.worker.base import FactIngestionPayload


class _FakeSession:
    def __init__(self) -> None:
        self.added: list[Any] = []
        self.committed = False
        self.flushed = False

    async def __aenter__(self) -> _FakeSession:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushed = True

    async def commit(self) -> None:
        self.committed = True


class _FakeDbManager:
    def __init__(self) -> None:
        self.session = _FakeSession()

    def get_session(self) -> _FakeSession:
        return self.session


class _DummyRefreshConnector(BaseRefreshConnector):
    def __init__(self, facts_to_return: list[dict[str, Any]], db_manager: _FakeDbManager | None = None) -> None:
        super().__init__(
            source_name="dummy_source",
            source_type="dummy_type",
            db_manager=db_manager,
            confidence=0.61,
        )
        self._facts_to_return = facts_to_return

    async def fetch_facts(
        self,
        company_ids: list[str],
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> list[dict[str, Any]]:
        return list(self._facts_to_return)

    async def _filter_delta(self, facts: list[dict[str, Any]], since: datetime) -> list[dict[str, Any]]:
        return facts

    async def _update_refresh_metadata(self, refresh_time: datetime) -> None:
        return None


def test_fact_ingestion_payload_normalizes_type_alias_and_metadata() -> None:
    payload = FactIngestionPayload.model_validate(
        {
            "company_id": "acme",
            "type": "market_metrics",
            "value": {"market_cap": 123},
            "metadata": None,
        }
    )

    assert payload.fact_type == "market_metrics"
    assert payload.metadata == {}
    assert payload.confidence == 0.5


@pytest.mark.asyncio
async def test_refresh_get_facts_to_refresh_rejects_invalid_payloads_before_delta() -> None:
    connector = _DummyRefreshConnector(
        facts_to_return=[
            {
                "company_id": "acme",
                "type": "market_metrics",
                "value": {"market_cap": 123},
                "metadata": None,
            },
            {
                "company_id": "acme",
                "value": {"market_cap": 456},
            },
            {
                "company_id": "",
                "fact_type": "market_metrics",
                "value": {"market_cap": 789},
            },
        ]
    )

    facts = await connector.get_facts_to_refresh(
        ["acme"],
        since=datetime(2026, 3, 26, tzinfo=timezone.utc),
    )

    assert len(facts) == 1
    assert facts[0]["fact_type"] == "market_metrics"
    assert facts[0]["metadata"] == {}
    assert facts[0]["confidence"] == 0.61


@pytest.mark.asyncio
async def test_refresh_store_facts_uses_validated_boundary_and_orm_compatible_batch() -> None:
    db_manager = _FakeDbManager()
    connector = _DummyRefreshConnector([], db_manager=db_manager)

    batch = await connector.store_facts(
        [
            {
                "company_id": "acme",
                "type": "employee_count",
                "value": 125,
            },
            {
                "fact_type": "employee_count",
                "value": 130,
            },
        ],
        batch_id="batch-123",
    )

    assert batch.company_id == "acme"
    assert batch.status == "completed"
    assert db_manager.session.flushed is True
    assert db_manager.session.committed is True
    assert len(db_manager.session.added) == 2

    stored_fact = db_manager.session.added[1]
    assert stored_fact.company_id == "acme"
    assert stored_fact.fact_type == "employee_count"
    assert float(stored_fact.value) == 125.0
    assert stored_fact.value_str is None
