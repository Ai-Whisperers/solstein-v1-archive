"""
Patent Data Client for Solstein - Robust Version

Multiple backends (tries in order until one works):
1. USPTO Patent Examination Data System (PEDS) - NO API KEY NEEDED
2. Google Patents via web scraping
3. DuckDuckGo web search fallback
"""

from typing import Any

from loguru import logger


class PatentResult:
    """Patent search result."""

    def __init__(
        self,
        total_patents: int = 0,
        recent_patents: list[dict[str, Any]] | None = None,
        ai_related_patents: int = 0,
        top_categories: list[str] | None = None,
        source: str = "none",
    ):
        self.total_patents = total_patents
        self.recent_patents = recent_patents if recent_patents is not None else []
        self.ai_related_patents = ai_related_patents
        self.top_categories = top_categories if top_categories is not None else []
        self.source = source


def search_company_patents(company_name: str) -> PatentResult:
    """
    Search for company patents using multiple backends.

    Tries each source in order until one succeeds.
    """
    result = _search_uspto_peds(company_name)
    if result.total_patents > 0:
        logger.info(
            f"Found {result.total_patents} patents via USPTO for {company_name}"
        )
        return result

    result = _search_google_patents(company_name)
    if result.total_patents > 0:
        logger.info(
            f"Found {result.total_patents} patents via Google Patents for {company_name}"
        )
        return result

    result = _search_duckduckgo(company_name)
    if result.total_patents > 0:
        logger.info(
            f"Found {result.total_patents} patents via DuckDuckGo for {company_name}"
        )
        return result

    return PatentResult(source="none")


def _search_uspto_peds(company_name: str) -> PatentResult:
    """
    Search USPTO Patent Examination Data System (PEDS).

    Free, no API key needed. Official USPTO API.
    """
    import httpx

    base_url = "https://developer.uspto.gov/ibd-api/v1/patent/application"

    params = {
        "searchText": company_name,
        "rows": 20,
        "start": 0,
    }

    try:
        response = httpx.get(base_url, params=params, timeout=30)

        if response.status_code != 200:
            logger.debug(f"USPTO PEDS returned {response.status_code}")
            return PatentResult()

        data = response.json()
        response_header = data.get("responseHeader", {})
        num_found = response_header.get("numFound", 0)

        if num_found == 0:
            return PatentResult()

        docs = data.get("response", {}).get("docs", [])

        ai_keywords = [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "neural network",
            "natural language processing",
            "computer vision",
            "nlp",
            "ml",
            "ai",
            "algorithm",
            "predictive",
            "automation",
        ]

        recent = []
        ai_count = 0

        for doc in docs[:10]:
            title = doc.get("application_title_text", "")
            title_lower = title.lower()

            if any(kw in title_lower for kw in ai_keywords):
                ai_count += 1

            recent.append(
                {
                    "patent_id": doc.get("application_number_text", ""),
                    "title": title,
                    "date": doc.get("filing_date", ""),
                    "abstract": doc.get("abstract_text", "")[:200]
                    if doc.get("abstract_text")
                    else None,
                }
            )

        return PatentResult(
            total_patents=num_found,
            recent_patents=recent,
            ai_related_patents=ai_count,
            source="uspto_peds",
        )

    except Exception as e:
        logger.debug(f"USPTO PEDS error: {e}")
        return PatentResult()


def _search_google_patents(company_name: str) -> PatentResult:
    """
    Search Google Patents via scraping.
    """
    import httpx
    from lxml import html

    query = company_name.replace(" ", "+")
    url = f"https://patents.google.com/?q={query}&num=20"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            return PatentResult()

        soup = html.fromstring(response.text)

        results = []
        for item in soup.cssselect("search-result-item"):
            try:
                title_elem = item.cssselect(".result-title")
                title = title_elem[0].text.strip() if title_elem else ""

                if title:
                    results.append({"title": title, "date": "", "url": ""})
            except Exception:
                continue

        if results:
            ai_keywords = [
                "ai",
                "machine learning",
                "artificial intelligence",
                "neural",
                "patent",
            ]
            ai_count = sum(
                1
                for r in results
                if any(kw in r.get("title", "").lower() for kw in ai_keywords)
            )

            return PatentResult(
                total_patents=len(results) * 5,
                recent_patents=results[:10],
                ai_related_patents=ai_count,
                source="google_patents",
            )

    except Exception as e:
        logger.debug(f"Google Patents error: {e}")

    return PatentResult()


def _search_duckduckgo(company_name: str) -> PatentResult:
    """
    Fallback: Use DuckDuckGo for patent-related information.
    """
    import httpx
    from lxml import html

    query = company_name.replace(" ", "+")
    url = f"https://html.duckduckgo.com/html/?q={query}+patents"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = httpx.get(url, headers=headers, timeout=15)
        soup = html.fromstring(response.text)

        results = []
        for item in soup.cssselect("a.result__a")[:15]:
            title = item.text_content().strip()
            href = str(item.get("href", ""))

            if title and href:
                results.append(
                    {
                        "title": title,
                        "url": href,
                    }
                )

        if results:
            ai_keywords = [
                "ai",
                "machine learning",
                "artificial intelligence",
                "neural",
                "patent",
            ]
            ai_count = sum(
                1
                for r in results
                if any(kw in r.get("title", "").lower() for kw in ai_keywords)
            )

            return PatentResult(
                total_patents=len(results) * 3,
                recent_patents=results[:10],
                ai_related_patents=ai_count,
                source="duckduckgo",
            )

    except Exception as e:
        logger.debug(f"DuckDuckGo patent error: {e}")

    return PatentResult()
