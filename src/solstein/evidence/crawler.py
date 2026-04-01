"""
Web Crawler - Intelligent web crawling for evidence collection.

This module provides web crawling capabilities for EPIC-041.

FREE tools used:
- Crawl4AI (open source)
- Playwright (browser automation)
- BeautifulSoup (HTML parsing)
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler, CacheMode, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

from .models import Claim, SourceType, create_claim

logger = logging.getLogger(__name__)


@dataclass
class CrawlResult:
    """Result of crawling a single URL."""

    url: str
    success: bool
    title: str | None = None
    content: str | None = None
    markdown: str | None = None
    links: list[str] = field(default_factory=list)
    error: str | None = None
    word_count: int = 0
    content_hash: str | None = None


class EvidenceCrawler:
    """
    Intelligent web crawler for collecting evidence from company websites.

    Uses Crawl4AI for high-quality content extraction.
    """

    def __init__(
        self,
        max_pages: int = 10,
        max_depth: int = 2,
        respect_robots: bool = True,
        delay: float = 1.0,
    ):
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.respect_robots = respect_robots
        self.delay = delay
        self._crawled_urls: set[str] = set()
        self._crawl_results: list[CrawlResult] = []

    async def crawl_company_website(
        self,
        company_id: str,
        start_url: str,
        page_types: list[str] | None = None,
        on_page_crawled: Callable[[CrawlResult], None] | None = None,
    ) -> list[CrawlResult]:
        """
        Crawl a company website starting from the given URL.

        Args:
            company_id: Unique identifier for the company
            start_url: Starting URL (usually homepage)
            page_types: List of page types to prioritize (about, careers, investors, etc.)
            on_page_crawled: Callback for each crawled page

        Returns:
            List of crawl results
        """
        self._crawled_urls.clear()
        self._crawl_results.clear()

        # Priority paths for company intelligence
        priority_paths = page_types or [
            "about",
            "company",
            "careers",
            "jobs",
            "investors",
            "press",
            "news",
            "blog",
            "products",
            "pricing",
        ]

        async with AsyncWebCrawler() as crawler:
            # Crawl homepage first
            await self._crawl_page(
                crawler,
                start_url,
                company_id,
                depth=0,
                on_page_crawled=on_page_crawled,
            )

            # Discover and crawl priority pages
            discovered = await self._discover_priority_pages(
                crawler,
                start_url,
                priority_paths,
            )

            for url in discovered[: self.max_pages - 1]:
                if url not in self._crawled_urls:
                    await self._crawl_page(
                        crawler,
                        url,
                        company_id,
                        depth=1,
                        on_page_crawled=on_page_crawled,
                    )
                    await asyncio.sleep(self.delay)

        return self._crawl_results

    async def _crawl_page(
        self,
        crawler: AsyncWebCrawler,
        url: str,
        company_id: str,
        depth: int = 0,
        on_page_crawled: Callable[[CrawlResult], None] | None = None,
    ) -> CrawlResult:
        """Crawl a single page."""
        if url in self._crawled_urls:
            return CrawlResult(url=url, success=False, error="Already crawled")

        if len(self._crawled_urls) >= self.max_pages:
            return CrawlResult(url=url, success=False, error="Max pages reached")

        self._crawled_urls.add(url)

        try:
            # Configure crawling
            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                markdown_generator=DefaultMarkdownGenerator(
                    content_filter=PruningContentFilter(threshold=0.5),
                ),
            )

            # Crawl
            result = await crawler.arun(url=url, config=config)

            if result.success:
                # Extract content
                # Extract content - Crawl4AI returns MarkdownGenerationResult
                if hasattr(result.markdown, "fit_markdown"):
                    # New API: markdown is MarkdownGenerationResult
                    content = result.markdown.fit_markdown or result.markdown.raw_markdown or ""
                else:
                    # Old API: markdown is string
                    content = result.markdown or ""

                # Calculate content hash
                content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

                # Count words
                word_count = len(content.split())

                # Extract links
                links = []
                if result.links:
                    links = [
                        urljoin(url, link["href"]) for link in result.links.get("internal", []) if link.get("href")
                    ]

                crawl_result = CrawlResult(
                    url=url,
                    success=True,
                    title=result.metadata.get("title") if result.metadata else None,
                    content=content,
                    markdown=content,
                    links=links,
                    word_count=word_count,
                    content_hash=content_hash,
                )

                logger.info(f"Crawled: {url} ({word_count} words)")

            else:
                crawl_result = CrawlResult(
                    url=url,
                    success=False,
                    error=result.error_message,
                )
                logger.warning(f"Failed to crawl: {url} - {result.error_message}")

            self._crawl_results.append(crawl_result)

            if on_page_crawled:
                on_page_crawled(crawl_result)

            return crawl_result

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            crawl_result = CrawlResult(
                url=url,
                success=False,
                error=str(e),
            )
            self._crawl_results.append(crawl_result)
            return crawl_result

    async def _discover_priority_pages(
        self,
        crawler: AsyncWebCrawler,
        start_url: str,
        priority_paths: list[str],
    ) -> list[str]:
        """Discover priority pages from the start URL."""
        try:
            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                only_text=True,
            )

            result = await crawler.arun(url=start_url, config=config)

            if not result.success or not result.links:
                return []

            discovered = []

            for link in result.links.get("internal", []):
                href = link.get("href", "")
                full_url = urljoin(start_url, href)

                # Check if URL contains priority path
                url_lower = full_url.lower()
                for path in priority_paths:
                    if path.lower() in url_lower:
                        discovered.append(full_url)
                        break

            # Remove duplicates while preserving order
            seen = set()
            unique = []
            for url in discovered:
                if url not in seen:
                    seen.add(url)
                    unique.append(url)

            return unique

        except Exception as e:
            logger.error(f"Error discovering pages: {e}")
            return []

    def extract_claims_from_content(
        self,
        crawl_result: CrawlResult,
        company_id: str,
        extraction_rules: dict | None = None,
    ) -> list[Claim]:
        """
        Extract claims from crawled content using regex patterns.

        This is a simple rule-based extractor. For production, use LLM-based extraction.
        """
        claims = []
        content = crawl_result.content or ""

        # Default extraction rules
        rules = extraction_rules or {
            "revenue": [
                r"revenue.*?(\d+[\d,]*\s*(?:million|billion|m|b)?)",
                r"(\$\d+[\d,]*\s*(?:million|billion|m|b)?).*?revenue",
            ],
            "employee_count": [
                r"(\d+)\s*employees",
                r"team\s*of\s*(\d+)",
                r"(\d+)\s*people",
            ],
            "founded_year": [
                r"founded\s*(?:in)?\s*(\d{4})",
                r"since\s*(\d{4})",
            ],
            "headquarters": [
                r"headquartered\s*(?:in)?\s*([^,.]+)",
                r"based\s*(?:in)?\s*([^,.]+)",
            ],
        }

        import re

        for field_name, patterns in rules.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    value = match.group(1).strip()

                    # Create claim
                    claim = create_claim(
                        entity_id=company_id,
                        field=field_name,
                        value=value,
                        source_url=crawl_result.url,
                        snippet=match.group(0),
                        source_type=SourceType.WEBSITE,
                        extraction_method="regex",
                    )

                    # Simple confidence based on pattern match quality
                    claim.overall_confidence = 0.6  # Regex-based extraction

                    claims.append(claim)

        logger.info(f"Extracted {len(claims)} claims from {crawl_result.url}")
        return claims


class SimpleCrawler:
    """
    Simple fallback crawler using requests + BeautifulSoup.

    Use when Crawl4AI is not available or for lightweight crawling.
    """

    def __init__(
        self,
        max_pages: int = 5,
        delay: float = 1.0,
        user_agent: str = "SolsteinBot/1.0 (Research Bot)",
    ):
        self.max_pages = max_pages
        self.delay = delay
        self.user_agent = user_agent

    def crawl(self, url: str) -> CrawlResult:
        """Simple synchronous crawl using requests."""
        import requests
        from bs4 import BeautifulSoup

        try:
            headers = {"User-Agent": self.user_agent}
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract title
            title = soup.title.string if soup.title else None

            # Extract text
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator="\n", strip=True)

            # Calculate hash
            content_hash = hashlib.sha256(text.encode()).hexdigest()[:16]

            # Count words
            word_count = len(text.split())

            # Extract links
            links = []
            base_domain = urlparse(url).netloc
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link["href"])
                if urlparse(full_url).netloc == base_domain:
                    links.append(full_url)

            return CrawlResult(
                url=url,
                success=True,
                title=title,
                content=text,
                links=links[:50],  # Limit links
                word_count=word_count,
                content_hash=content_hash,
            )

        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return CrawlResult(
                url=url,
                success=False,
                error=str(e),
            )


if __name__ == "__main__":
    # Test the crawler
    async def test_crawler():
        crawler = EvidenceCrawler(max_pages=3)

        results = await crawler.crawl_company_website(
            company_id="test-company",
            start_url="https://example.com",  # Replace with real URL for testing
        )

        print(f"Crawled {len(results)} pages")
        for r in results:
            print(f"  - {r.url}: {r.word_count} words, success={r.success}")

    # Run test
    asyncio.run(test_crawler())
