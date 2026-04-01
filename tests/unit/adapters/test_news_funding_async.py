"""Tests for STORY-134: httpx migration in news and funding adapters.

Verifies:
- No `import requests` in modified adapters
- Sync methods use httpx.get (not requests.get)
- Async methods use httpx.AsyncClient
- fetch_facts uses asyncio.gather for concurrency
- Exception handling catches httpx-specific errors
"""

import ast
import asyncio
import inspect
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

import solstein.adapters.enrichment._retired.funding_unified as funding_mod
import solstein.adapters.enrichment._retired.news_unified as news_mod
from solstein.adapters.enrichment._retired.funding_unified import FundingUnifiedAdapter
from solstein.adapters.enrichment._retired.news_unified import NewsUnifiedAdapter

# ---------------------------------------------------------------------------
# 1. No `requests` import
# ---------------------------------------------------------------------------

class TestNoRequestsImport:
    """Ensure neither adapter imports the `requests` library."""

    def test_news_unified_no_requests(self):
        source = inspect.getsource(news_mod)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "requests", "news_unified still imports requests"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "requests", "news_unified still imports from requests"

    def test_funding_unified_no_requests(self):
        source = inspect.getsource(funding_mod)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "requests", "funding_unified still imports requests"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "requests", "funding_unified still imports from requests"


# ---------------------------------------------------------------------------
# 2. Async method signatures
# ---------------------------------------------------------------------------

class TestAsyncSignatures:
    """Verify async methods exist and are coroutines."""

    def test_news_get_news_from_api_async_is_coroutine(self):
        adapter = NewsUnifiedAdapter.__new__(NewsUnifiedAdapter)
        assert asyncio.iscoroutinefunction(adapter._get_news_from_api_async)

    def test_news_fetch_facts_is_coroutine(self):
        adapter = NewsUnifiedAdapter.__new__(NewsUnifiedAdapter)
        assert asyncio.iscoroutinefunction(adapter.fetch_facts)

    def test_funding_get_crunchbase_data_async_is_coroutine(self):
        adapter = FundingUnifiedAdapter.__new__(FundingUnifiedAdapter)
        assert asyncio.iscoroutinefunction(adapter._get_crunchbase_data_async)

    def test_funding_fetch_facts_is_coroutine(self):
        adapter = FundingUnifiedAdapter.__new__(FundingUnifiedAdapter)
        assert asyncio.iscoroutinefunction(adapter.fetch_facts)


# ---------------------------------------------------------------------------
# 3. NewsUnifiedAdapter - sync httpx usage
# ---------------------------------------------------------------------------

class TestNewsSyncHttpx:
    """Test that sync path uses httpx.get."""

    @patch("solstein.adapters.enrichment.news_unified.get_settings")
    @patch("solstein.adapters.enrichment.news_unified.httpx.get")
    def test_get_news_from_api_uses_httpx(self, mock_get: MagicMock, mock_settings: MagicMock):
        mock_settings.return_value.http_timeouts.news_api = 10.0
        mock_response = MagicMock()
        mock_response.json.return_value = {"articles": []}
        mock_get.return_value = mock_response

        adapter = NewsUnifiedAdapter.__new__(NewsUnifiedAdapter)
        adapter.news_api_key = "test-key"
        adapter.source_name = "news_unified"

        result = adapter._get_news_from_api("TestCorp")
        assert isinstance(result, list)
        mock_get.assert_called_once()

    def test_get_news_from_api_no_key_returns_empty(self):
        adapter = NewsUnifiedAdapter.__new__(NewsUnifiedAdapter)
        adapter.news_api_key = None
        assert adapter._get_news_from_api("TestCorp") == []


# ---------------------------------------------------------------------------
# 4. NewsUnifiedAdapter - async httpx usage
# ---------------------------------------------------------------------------

class TestNewsAsyncHttpx:
    """Test that async path uses httpx.AsyncClient."""

    @pytest.mark.asyncio
    async def test_get_news_from_api_async_no_key_returns_empty(self):
        adapter = NewsUnifiedAdapter.__new__(NewsUnifiedAdapter)
        adapter.news_api_key = None
        result = await adapter._get_news_from_api_async("TestCorp")
        assert result == []

    @pytest.mark.asyncio
    @patch("solstein.adapters.enrichment.news_unified.get_settings")
    async def test_get_news_from_api_async_uses_async_client(self, mock_settings: MagicMock):
        mock_settings.return_value.http_timeouts.news_api = 10.0

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "articles": [
                {
                    "title": "TestCorp raises $10M",
                    "description": "Growth and expansion",
                    "source": {"name": "TechNews"},
                    "url": "https://example.com/article",
                    "publishedAt": "2026-03-01T12:00:00Z",
                }
            ]
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("solstein.adapters.enrichment.news_unified.httpx.AsyncClient", return_value=mock_client):
            adapter = NewsUnifiedAdapter.__new__(NewsUnifiedAdapter)
            adapter.news_api_key = "test-key"
            adapter.source_name = "news_unified"
            result = await adapter._get_news_from_api_async("TestCorp")

        assert len(result) == 1
        assert result[0]["title"] == "TestCorp raises $10M"
        assert result[0]["sentiment"] in ("positive", "negative", "neutral")


# ---------------------------------------------------------------------------
# 5. News fetch_facts uses asyncio.gather (concurrency check)
# ---------------------------------------------------------------------------

class TestNewsFetchFactsConcurrency:
    """Verify fetch_facts runs fetches concurrently via asyncio.gather."""

    @pytest.mark.asyncio
    @patch("solstein.adapters.enrichment.news_unified.get_settings")
    async def test_fetch_facts_concurrent(self, mock_settings: MagicMock):
        mock_settings.return_value.http_timeouts.news_api = 10.0
        delay_seconds = 0.05

        async def slow_get(*args: Any, **kwargs: Any) -> MagicMock:
            await asyncio.sleep(delay_seconds)
            resp = MagicMock()
            resp.json.return_value = {
                "articles": [
                    {
                        "title": "Article",
                        "description": "Desc",
                        "source": {"name": "Src"},
                        "url": "https://example.com",
                        "publishedAt": "2026-03-01T00:00:00Z",
                    }
                ]
            }
            return resp

        mock_client = AsyncMock()
        mock_client.get = slow_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("solstein.adapters.enrichment.news_unified.httpx.AsyncClient", return_value=mock_client):
            adapter = NewsUnifiedAdapter.__new__(NewsUnifiedAdapter)
            adapter.news_api_key = "test-key"
            adapter.source_name = "news_unified"
            adapter.confidence = 0.70

            company_ids = ["CompA", "CompB", "CompC", "CompD"]
            start = time.monotonic()
            facts = await adapter.fetch_facts(company_ids)
            elapsed = time.monotonic() - start

        assert len(facts) == 4
        # 4 fetches at 50ms each: concurrent < 150ms, sequential ~ 200ms+
        assert elapsed < 0.15, f"fetch_facts took {elapsed:.3f}s — likely sequential, not concurrent"

    @pytest.mark.asyncio
    async def test_fetch_facts_handles_exceptions(self):
        """fetch_facts should log and skip failed companies, not raise."""
        adapter = NewsUnifiedAdapter.__new__(NewsUnifiedAdapter)
        adapter.news_api_key = "test-key"
        adapter.source_name = "news_unified"
        adapter.confidence = 0.70

        async def exploding_fetch(*args: Any, **kwargs: Any) -> list:
            raise httpx.ConnectError("connection refused")

        with patch.object(adapter, "_get_news_from_api_async", side_effect=exploding_fetch):
            facts = await adapter.fetch_facts(["CompA", "CompB"])

        assert facts == []  # all failed, none returned


# ---------------------------------------------------------------------------
# 6. FundingUnifiedAdapter - sync httpx usage
# ---------------------------------------------------------------------------

class TestFundingSyncHttpx:
    """Test that sync path uses httpx.get."""

    @patch("solstein.adapters.enrichment._retired.funding_unified.get_settings")
    @patch("solstein.adapters.enrichment._retired.funding_unified.httpx.get")
    def test_get_crunchbase_data_uses_httpx(self, mock_get: MagicMock, mock_settings: MagicMock):
        mock_settings.return_value.http_timeouts.funding = 10.0
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "properties": {
                "total_funding": 5000000,
                "last_funding_amount": 2000000,
                "last_funded_at": "2026-01-15",
                "last_funding_stage": "Series A",
                "valuation": 20000000,
                "funding_rounds": 2,
            }
        }
        mock_get.return_value = mock_response

        adapter = FundingUnifiedAdapter.__new__(FundingUnifiedAdapter)
        adapter.crunchbase_api_key = "test-key"
        adapter.source_name = "funding_unified"

        result = adapter._get_crunchbase_data("TestCorp")
        assert result is not None
        assert result["total_raised"] == 5000000
        assert result["num_rounds"] == 2
        mock_get.assert_called_once()

    def test_get_crunchbase_data_no_key_returns_none(self):
        adapter = FundingUnifiedAdapter.__new__(FundingUnifiedAdapter)
        adapter.crunchbase_api_key = None
        assert adapter._get_crunchbase_data("TestCorp") is None


# ---------------------------------------------------------------------------
# 7. FundingUnifiedAdapter - async httpx usage
# ---------------------------------------------------------------------------

class TestFundingAsyncHttpx:
    """Test that async path uses httpx.AsyncClient."""

    @pytest.mark.asyncio
    async def test_get_crunchbase_data_async_no_key_returns_none(self):
        adapter = FundingUnifiedAdapter.__new__(FundingUnifiedAdapter)
        adapter.crunchbase_api_key = None
        result = await adapter._get_crunchbase_data_async("TestCorp")
        assert result is None

    @pytest.mark.asyncio
    @patch("solstein.adapters.enrichment._retired.funding_unified.get_settings")
    async def test_get_crunchbase_data_async_returns_data(self, mock_settings: MagicMock):
        mock_settings.return_value.http_timeouts.funding = 10.0

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "properties": {
                "total_funding": 5000000,
                "last_funding_amount": 2000000,
                "last_funded_at": "2026-01-15",
                "last_funding_stage": "Series A",
                "valuation": 20000000,
                "funding_rounds": 2,
            }
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("solstein.adapters.enrichment._retired.funding_unified.httpx.AsyncClient", return_value=mock_client):
            adapter = FundingUnifiedAdapter.__new__(FundingUnifiedAdapter)
            adapter.crunchbase_api_key = "test-key"
            adapter.source_name = "funding_unified"
            result = await adapter._get_crunchbase_data_async("TestCorp")

        assert result is not None
        assert result["total_raised"] == 5000000


# ---------------------------------------------------------------------------
# 8. Funding fetch_facts concurrency
# ---------------------------------------------------------------------------

class TestFundingFetchFactsConcurrency:
    """Verify fetch_facts runs fetches concurrently via asyncio.gather."""

    @pytest.mark.asyncio
    @patch("solstein.adapters.enrichment._retired.funding_unified.get_settings")
    async def test_fetch_facts_concurrent(self, mock_settings: MagicMock):
        mock_settings.return_value.http_timeouts.funding = 10.0
        delay_seconds = 0.05

        async def slow_get(*args: Any, **kwargs: Any) -> MagicMock:
            await asyncio.sleep(delay_seconds)
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {
                "properties": {
                    "total_funding": 1000000,
                    "last_funding_amount": 500000,
                    "last_funded_at": "2026-01-01",
                    "last_funding_stage": "Seed",
                    "valuation": 5000000,
                    "funding_rounds": 1,
                }
            }
            return resp

        mock_client = AsyncMock()
        mock_client.get = slow_get
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("solstein.adapters.enrichment._retired.funding_unified.httpx.AsyncClient", return_value=mock_client):
            adapter = FundingUnifiedAdapter.__new__(FundingUnifiedAdapter)
            adapter.crunchbase_api_key = "test-key"
            adapter.source_name = "funding_unified"
            adapter.confidence = 0.65

            company_ids = ["CompA", "CompB", "CompC", "CompD"]
            start = time.monotonic()
            facts = await adapter.fetch_facts(company_ids)
            elapsed = time.monotonic() - start

        assert len(facts) == 4
        assert elapsed < 0.15, f"fetch_facts took {elapsed:.3f}s — likely sequential, not concurrent"

    @pytest.mark.asyncio
    async def test_fetch_facts_handles_exceptions(self):
        """fetch_facts should log and skip failed companies, not raise."""
        adapter = FundingUnifiedAdapter.__new__(FundingUnifiedAdapter)
        adapter.crunchbase_api_key = "test-key"
        adapter.source_name = "funding_unified"
        adapter.confidence = 0.65

        async def exploding_fetch(*args: Any, **kwargs: Any) -> None:
            raise httpx.ConnectError("connection refused")

        with patch.object(adapter, "_get_crunchbase_data_async", side_effect=exploding_fetch):
            facts = await adapter.fetch_facts(["CompA", "CompB"])

        assert facts == []


# ---------------------------------------------------------------------------
# 9. Sentiment analysis (news adapter utility)
# ---------------------------------------------------------------------------

class TestSentimentAnalysis:
    """Verify simple sentiment analysis still works after migration."""

    def test_positive_sentiment(self):
        adapter = NewsUnifiedAdapter.__new__(NewsUnifiedAdapter)
        assert adapter._analyze_sentiment("Revenue growth and strong profit beat expectations") == "positive"

    def test_negative_sentiment(self):
        adapter = NewsUnifiedAdapter.__new__(NewsUnifiedAdapter)
        assert adapter._analyze_sentiment("Lawsuit and bankruptcy amid investigation and decline") == "negative"

    def test_neutral_sentiment(self):
        adapter = NewsUnifiedAdapter.__new__(NewsUnifiedAdapter)
        assert adapter._analyze_sentiment("Company announced quarterly results today") == "neutral"
