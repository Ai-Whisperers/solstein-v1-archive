"""
Web Search Client for Solstein.

Provides web search capabilities using multiple backends:
- Exa (primary)
- Google Search (fallback)

This enables news gathering without requiring NewsAPI keys.
"""

from typing import Any

from loguru import logger


def search_company_news(company_name: str, max_results: int = 20) -> list[dict[str, Any]]:
    """
    Search for company news using web search.

    Args:
        company_name: Name of the company to search for
        max_results: Maximum number of results to return

    Returns:
        List of news articles with title, snippet, url, date
    """
    try:
        from exa_py import Exa

        exa = Exa()
        results = exa.search_and_contents(
            query=f"{company_name} news 2025",
            num_results=max_results,
            text=True,
            start_published_date="2025-01-01",
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
        logger.warning("Exa not installed, trying Google fallback")
    except Exception as e:
        logger.error(f"Exa search error: {e}")

    return _google_search_fallback(company_name, max_results)


def _google_search_fallback(company_name: str, max_results: int = 20) -> list[dict[str, Any]]:
    """
    Fallback using Google Search if Exa is unavailable.
    """
    try:
        from google_search import google_search

        query = f"{company_name} latest news 2025"
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
    except Exception as e:
        logger.error(f"Google search error: {e}")

    return []


def search_company_info(company_name: str, query_type: str = "general") -> list[dict[str, Any]]:
    """
    Search for general company information.

    Args:
        company_name: Name of the company
        query_type: Type of search - "general", "funding", "product", "technology"

    Returns:
        List of search results
    """
    queries = {
        "general": f"{company_name} company overview",
        "funding": f"{company_name} funding rounds investment",
        "product": f"{company_name} products services software",
        "technology": f"{company_name} technology stack AI",
    }

    query = queries.get(query_type, queries["general"])

    try:
        from exa_py import Exa

        exa = Exa()
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

        return items

    except ImportError:
        logger.warning("Exa not installed for company info search")
    except Exception as e:
        logger.error(f"Company info search error: {e}")

    return []
