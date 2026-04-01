"""Regression tests for blocking sync work inside async code paths."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from solstein.adapters.enrichment._retired.patents_unified import PatentsUnifiedAdapter
from solstein.data.web_research_pipeline import WebResearcher
from solstein.infrastructure.connectors.news_signal_refresh import NewsSignalRefreshConnector
from solstein.infrastructure.connectors.web_search_refresh import WebSearchRefreshConnector


@pytest.mark.asyncio
async def test_patents_unified_fetch_facts_offloads_sync_patent_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    adapter = PatentsUnifiedAdapter()
    mock_search = MagicMock(
        return_value=SimpleNamespace(
            total_patents=4,
            recent_patents=[],
            ai_related_patents=1,
            top_categories=["ai"],
            source="uspto_peds",
        )
    )
    calls: list[tuple[object, tuple[object, ...], dict[str, object]]] = []

    async def fake_to_thread(func, *args, **kwargs):
        calls.append((func, args, kwargs))
        return func(*args, **kwargs)

    monkeypatch.setattr("solstein.adapters.enrichment.patents_unified.search_company_patents", mock_search)
    monkeypatch.setattr("solstein.adapters.enrichment.patents_unified.asyncio.to_thread", fake_to_thread)

    facts = await adapter.fetch_facts(["acme"])

    assert len(facts) == 2
    assert calls
    assert calls[0][0] is mock_search
    assert calls[0][1] == ("acme",)


@pytest.mark.asyncio
async def test_web_search_refresh_offloads_sync_search_client(monkeypatch: pytest.MonkeyPatch) -> None:
    connector = WebSearchRefreshConnector(MagicMock(), exa_api_key="test-key")
    mock_search = MagicMock(return_value=[{"title": "Acme", "url": "https://example.com"}])
    calls: list[tuple[object, tuple[object, ...], dict[str, object]]] = []

    async def fake_to_thread(func, *args, **kwargs):
        calls.append((func, args, kwargs))
        return func(*args, **kwargs)

    monkeypatch.setattr("solstein.data.web_search_client.search_company_info", mock_search)
    monkeypatch.setattr("solstein.infrastructure.connectors.web_search_refresh.asyncio.to_thread", fake_to_thread)

    facts = await connector.fetch_facts(["acme"])

    assert len(facts) == 1
    assert calls
    assert calls[0][0] is mock_search
    assert calls[0][1] == ("acme",)
    assert calls[0][2] == {"query_type": "general"}


@pytest.mark.asyncio
async def test_news_signal_refresh_awaits_detector_methods(monkeypatch: pytest.MonkeyPatch) -> None:
    signal = SimpleNamespace(
        signal_type="funding",
        description="Raised a round",
        source="newsapi",
        confidence=0.8,
        company_name="acme",
        raw_data={"title": "Acme raises", "url": "https://example.com", "published_at": "2026-03-26"},
    )
    detector = SimpleNamespace(
        detect_funding_signal=AsyncMock(return_value=[signal]),
        detect_partnership_signal=AsyncMock(return_value=[]),
        detect_key_hire_signal=AsyncMock(return_value=[]),
    )

    monkeypatch.setattr(
        "solstein.infrastructure.connectors.news_signal_refresh.NewsSignalDetector",
        lambda: detector,
    )

    connector = NewsSignalRefreshConnector(MagicMock())
    facts = await connector.fetch_facts(["acme-company"])

    assert len(facts) == 1
    detector.detect_funding_signal.assert_awaited_once_with("acme")
    detector.detect_partnership_signal.assert_awaited_once_with("acme")
    detector.detect_key_hire_signal.assert_awaited_once_with("acme")


@pytest.mark.asyncio
async def test_web_researcher_search_web_offloads_duckduckgo(monkeypatch: pytest.MonkeyPatch) -> None:
    researcher = WebResearcher()
    mock_search = MagicMock(return_value=[{"title": "Acme", "href": "https://example.com", "body": "Acme overview"}])
    calls: list[tuple[object, tuple[object, ...], dict[str, object]]] = []

    async def fake_to_thread(func, *args, **kwargs):
        calls.append((func, args, kwargs))
        return func(*args, **kwargs)

    monkeypatch.setattr(researcher, "_search_web_sync", mock_search)
    monkeypatch.setattr("solstein.data.web_research_pipeline.asyncio.to_thread", fake_to_thread)

    results = await researcher.search_web("acme")
    await researcher.__aexit__()

    assert results == [{"title": "Acme", "href": "https://example.com", "body": "Acme overview"}]
    assert calls
    assert calls[0][0] is mock_search
    assert calls[0][1] == ("acme",)
