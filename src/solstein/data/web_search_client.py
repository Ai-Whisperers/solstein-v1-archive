import importlib
import os
from datetime import datetime, timezone
from typing import Any

from loguru import logger


def _current_year() -> str:
    return str(datetime.now(tz=timezone.utc).year)


def _ddg_search_fallback(query: str, max_results: int = 20) -> list[dict[str, Any]]:
    """Fallback search using DuckDuckGo.

    Tries both 'ddgs' and 'duckduckgo_search' module names for compatibility."""
    # Try both module names for compatibility
    ddgs_cls = None

    try:
        ddgs_module = importlib.import_module("duckduckgo_search")
        ddgs_cls = ddgs_module.DDGS
    except Exception:  # noqa: BLE001
        try:
            ddgs_module = importlib.import_module("ddgs")
            ddgs_cls = ddgs_module.DDGS
        except Exception as e:  # noqa: BLE001
            logger.warning(f"DuckDuckGo module not available: {e}")
            return []

    if ddgs_cls is None:
        return []

    try:
        with ddgs_cls() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        items = []
        for result in results:
            url = result.get("href") or result.get("url") or ""
            items.append(
                {
                    "title": result.get("title", ""),
                    "snippet": (result.get("body") or result.get("snippet") or "")[:500],
                    "url": url,
                    "date": None,
                    "source": url.split("/")[2] if "/" in url else "Web",
                }
            )
        return items
    except Exception as e:  # noqa: BLE001
        logger.error(f"DDG search error: {e}")
        return []
    try:
        ddgs_module = importlib.import_module("ddgs")
        ddgs_cls = ddgs_module.DDGS

        with ddgs_cls() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        items = []
        for result in results:
            url = result.get("href") or result.get("url") or ""
            items.append(
                {
                    "title": result.get("title", ""),
                    "snippet": (result.get("body") or result.get("snippet") or "")[:500],
                    "url": url,
                    "date": None,
                    "source": url.split("/")[2] if "/" in url else "Web",
                }
            )
        return items
    except Exception as e:  # noqa: BLE001
        logger.error(f"DDG search error: {e}")
        return []


def _google_search_fallback(company_name: str, max_results: int = 20) -> list[dict[str, Any]]:
    try:
        google_module = importlib.import_module("google_search")
        google_search = google_module.google_search

        query = f"{company_name} latest news {_current_year()}"
        results = google_search(query, num_results=max_results)

        news_items = []
        for result in results:
            news_items.append(
                {
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", "")[:500],
                    "url": result.get("url", ""),
                    "date": None,
                    "source": result.get("url", "").split("/")[2] if "url" in result else "Web",
                }
            )

        if news_items:
            logger.info(f"Found {len(news_items)} news articles via Google for {company_name}")
        return news_items

    except ImportError:
        logger.warning("Google search not available")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Google search error: {e}")

    return []


def search_company_news(company_name: str, max_results: int = 20) -> list[dict[str, Any]]:
    exa_api_key = os.getenv("EXA_API_KEY")
    if not exa_api_key:
        google_results = _google_search_fallback(company_name, max_results)
        if google_results:
            return google_results
        return _ddg_search_fallback(f"{company_name} latest news {_current_year()}", max_results=max_results)

    try:
        exa_module = importlib.import_module("exa_py")
        exa_cls = exa_module.Exa

        exa = exa_cls(api_key=exa_api_key)
        results = exa.search_and_contents(
            query=f"{company_name} news {_current_year()}",
            num_results=max_results,
            text=True,
            start_published_date=f"{_current_year()}-01-01",
        )

        news_items = []
        for result in results.results:
            news_items.append(
                {
                    "title": result.title,
                    "snippet": result.text[:500] if result.text else "",
                    "url": result.url,
                    "date": result.published_date,
                    "source": result.url.split("/")[2] if len(result.url.split("/")) > 2 else "Web",
                }
            )

        if news_items:
            logger.info(f"Found {len(news_items)} news articles via Exa for {company_name}")
            return news_items

    except ImportError:
        logger.warning("Exa not installed, trying fallback chain")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Exa search error: {e}")

    google_results = _google_search_fallback(company_name, max_results)
    if google_results:
        return google_results

    ddg_query = f"{company_name} latest news {_current_year()}"
    ddg_results = _ddg_search_fallback(ddg_query, max_results=max_results)
    if ddg_results:
        logger.info(f"Found {len(ddg_results)} news articles via DDG for {company_name}")
    return ddg_results


def search_company_info(company_name: str, query_type: str = "general") -> list[dict[str, Any]]:
    queries = {
        "general": f"{company_name} company overview",
        "funding": f"{company_name} funding rounds investment",
        "product": f"{company_name} products services software",
        "technology": f"{company_name} technology stack AI",
    }

    query = queries.get(query_type, queries["general"])

    exa_api_key = os.getenv("EXA_API_KEY")
    if not exa_api_key:
        ddg_results = _ddg_search_fallback(query, max_results=10)
        if ddg_results:
            logger.info(f"Found {len(ddg_results)} company info results via DDG for {company_name}")
        return ddg_results

    try:
        exa_module = importlib.import_module("exa_py")
        exa_cls = exa_module.Exa

        exa = exa_cls(api_key=exa_api_key)
        results = exa.search_and_contents(
            query=query,
            num_results=10,
            text=True,
        )

        items = []
        for result in results.results:
            items.append(
                {
                    "title": result.title,
                    "snippet": result.text[:500] if result.text else "",
                    "url": result.url,
                }
            )

        if items:
            logger.info(f"Found {len(items)} company info results via Exa for {company_name}")
            return items

    except ImportError:
        logger.warning("Exa not installed for company info search")
    except Exception as e:  # noqa: BLE001
        logger.error(f"Company info search error: {e}")

    ddg_results = _ddg_search_fallback(query, max_results=10)
    if ddg_results:
        logger.info(f"Found {len(ddg_results)} company info results via DDG for {company_name}")
    return ddg_results
