"""Tests for STORY-135: httpx migration in Companies House, Website agents, and Website adapter.

Verifies:
- No `import requests` in modified files
- Async methods use httpx.AsyncClient (no asyncio.to_thread wrapping sync httpx)
- fetch_facts uses asyncio.gather for concurrency in website_unified
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

import solstein.adapters.enrichment._retired.website_unified as website_adapter_mod
import solstein.agents.companies_house_agent as ch_mod
import solstein.agents.website_agent as web_mod
from solstein.adapters.enrichment._retired.website_unified import WebsiteUnifiedAdapter
from solstein.agents.companies_house_agent import CompaniesHouseAgent
from solstein.agents.website_agent import WebsiteAgent

# ---------------------------------------------------------------------------
# 1. No `requests` import
# ---------------------------------------------------------------------------

class TestNoRequestsImport:
    """Ensure no modified file imports the `requests` library."""

    @pytest.mark.parametrize("module", [web_mod, ch_mod, website_adapter_mod])
    def test_no_requests_import(self, module: Any):
        source = inspect.getsource(module)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "requests", f"{module.__name__} still imports requests"
            elif isinstance(node, ast.ImportFrom):
                assert node.module != "requests", f"{module.__name__} still imports from requests"


# ---------------------------------------------------------------------------
# 2. No asyncio.to_thread in companies_house_agent
# ---------------------------------------------------------------------------

class TestNoToThread:
    """Verify Companies House no longer uses asyncio.to_thread."""

    def test_no_to_thread_call_in_companies_house(self):
        """Verify no actual asyncio.to_thread() calls in companies_house_agent (docstrings OK)."""
        source = inspect.getsource(ch_mod)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "to_thread":
                pytest.fail("companies_house_agent still calls asyncio.to_thread")

    def test_no_to_thread_call_in_website_unified(self):
        """Verify no actual asyncio.to_thread() calls in website_unified (docstrings OK)."""
        source = inspect.getsource(website_adapter_mod)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "to_thread":
                pytest.fail("website_unified still calls asyncio.to_thread")


# ---------------------------------------------------------------------------
# 3. Async signatures
# ---------------------------------------------------------------------------

class TestAsyncSignatures:
    """Verify key methods are async coroutines."""

    def test_ch_api_search_company_is_coroutine(self):
        assert asyncio.iscoroutinefunction(CompaniesHouseAgent._api_search_company)

    def test_ch_api_get_company_is_coroutine(self):
        assert asyncio.iscoroutinefunction(CompaniesHouseAgent._api_get_company)

    def test_ch_api_get_financials_is_coroutine(self):
        assert asyncio.iscoroutinefunction(CompaniesHouseAgent._api_get_financials)

    def test_website_unified_scrape_async_is_coroutine(self):
        adapter = WebsiteUnifiedAdapter.__new__(WebsiteUnifiedAdapter)
        assert asyncio.iscoroutinefunction(adapter._scrape_website_async)

    def test_website_unified_fetch_facts_is_coroutine(self):
        adapter = WebsiteUnifiedAdapter.__new__(WebsiteUnifiedAdapter)
        assert asyncio.iscoroutinefunction(adapter.fetch_facts)


# ---------------------------------------------------------------------------
# 4. WebsiteAgent uses httpx.AsyncClient
# ---------------------------------------------------------------------------

class TestWebsiteAgentAsync:
    """Test that WebsiteAgent uses httpx.AsyncClient."""

    @pytest.mark.asyncio
    async def test_gather_uses_async_client(self):
        mock_response = MagicMock()
        mock_response.text = "<html><title>TestCorp</title></html>"
        mock_response.status_code = 200
        mock_response.url = "https://testcorp.com"

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("solstein.agents.website_agent.httpx.AsyncClient", return_value=mock_client):
            with patch("solstein.agents.website_agent.validate_url"):
                agent = WebsiteAgent()
                result = await agent.gather("TestCorp", {"website": "https://testcorp.com"})

        assert result.success is True
        assert len(result.extracted_facts) >= 1  # at least the title fact

    @pytest.mark.asyncio
    async def test_gather_no_url_returns_error(self):
        agent = WebsiteAgent()
        result = await agent.gather("TestCorp", {})
        assert result.success is False
        assert "missing" in (result.error_message or "").lower()


# ---------------------------------------------------------------------------
# 5. CompaniesHouseAgent async API methods
# ---------------------------------------------------------------------------

class TestCompaniesHouseAsync:
    """Test that Companies House _api_* methods use httpx.AsyncClient."""

    @pytest.mark.asyncio
    async def test_api_search_company_uses_async_client(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"company_number": "12345678", "title": "TestCorp Ltd"}]
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("solstein.agents.companies_house_agent.httpx.AsyncClient", return_value=mock_client):
            with patch("solstein.agents.companies_house_agent._get_settings") as mock_settings:
                mock_settings.return_value.companies_house_api_key = "test-key"
                mock_settings.return_value.http_timeouts.companies_house = 10.0
                mock_settings.return_value.circuit_breaker.failure_threshold = 5
                mock_settings.return_value.circuit_breaker.recovery_timeout = 30
                agent = CompaniesHouseAgent()
                result = await agent._api_search_company("TestCorp")

        assert result == "12345678"

    @pytest.mark.asyncio
    async def test_api_get_company_uses_async_client(self):
        expected_data = {"company_name": "TestCorp Ltd", "company_status": "active"}
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("solstein.agents.companies_house_agent.httpx.AsyncClient", return_value=mock_client):
            with patch("solstein.agents.companies_house_agent._get_settings") as mock_settings:
                mock_settings.return_value.companies_house_api_key = "test-key"
                mock_settings.return_value.http_timeouts.companies_house = 10.0
                mock_settings.return_value.circuit_breaker.failure_threshold = 5
                mock_settings.return_value.circuit_breaker.recovery_timeout = 30
                agent = CompaniesHouseAgent()
                result = await agent._api_get_company("12345678")

        assert result == expected_data


# ---------------------------------------------------------------------------
# 6. WebsiteUnifiedAdapter concurrency
# ---------------------------------------------------------------------------

class TestWebsiteUnifiedConcurrency:
    """Verify fetch_facts runs fetches concurrently via asyncio.gather."""

    @pytest.mark.asyncio
    async def test_fetch_facts_concurrent(self):
        delay_seconds = 0.05

        async def slow_scrape(website: str) -> dict[str, Any]:
            await asyncio.sleep(delay_seconds)
            return {
                "main_products": ["software"],
                "tech_stack": ["python"],
                "product_count": 1,
                "tech_count": 1,
            }

        adapter = WebsiteUnifiedAdapter.__new__(WebsiteUnifiedAdapter)
        adapter.source_name = "website_unified"
        adapter.confidence = 0.70

        with patch.object(adapter, "_scrape_website_async", side_effect=slow_scrape):
            company_ids = ["CompA", "CompB", "CompC", "CompD"]
            start = time.monotonic()
            facts = await adapter.fetch_facts(company_ids)
            elapsed = time.monotonic() - start

        assert len(facts) == 4
        assert elapsed < 0.15, f"fetch_facts took {elapsed:.3f}s — likely sequential"

    @pytest.mark.asyncio
    async def test_fetch_facts_handles_exceptions(self):
        adapter = WebsiteUnifiedAdapter.__new__(WebsiteUnifiedAdapter)
        adapter.source_name = "website_unified"
        adapter.confidence = 0.70

        async def exploding_scrape(website: str) -> dict[str, Any]:
            raise httpx.ConnectError("connection refused")

        with patch.object(adapter, "_scrape_website_async", side_effect=exploding_scrape):
            facts = await adapter.fetch_facts(["CompA", "CompB"])

        assert facts == []
