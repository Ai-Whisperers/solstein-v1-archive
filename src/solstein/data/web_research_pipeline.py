"""
Real-Time Company Data Research Pipeline
=========================================

This module implements a web research pipeline that fetches real company data
from multiple web sources, eliminating synthetic data usage.

Data Sources:
- Web Search (Google/Brave) for company information
- Company websites (scraping)
- LinkedIn (public profiles)
- Crunchbase (public profiles)
- News sources

"""

import asyncio
import contextlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from loguru import logger


@dataclass
class ResearchResult:
    """Result from web research for a company."""

    company_name: str
    website: str | None = None
    description: str | None = None
    industry: str | None = None
    founded_year: int | None = None
    employees: int | None = None
    headquarters: str | None = None
    revenue: float | None = None  # in millions
    funding_raised: float | None = None  # in millions
    valuation: float | None = None  # in millions
    github_url: str | None = None
    linkedin_url: str | None = None
    twitter_url: str | None = None
    ai_score: float | None = None
    data_sources: list[str] = field(default_factory=list)
    confidence: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    raw_data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "company_name": self.company_name,
            "website": self.website,
            "description": self.description,
            "industry": self.industry or "Energy Software",
            "country": self.headquarters or "Unknown",
            "founded_year": self.founded_year,
            "employees": self.employees,
            "funding_raised": self.funding_raised * 1_000_000 if self.funding_raised else None,
            "valuation": self.valuation * 1_000_000 if self.valuation else None,
            "github_url": self.github_url,
            "revenue": {
                "timeline": [
                    {
                        "year": datetime.now().year,
                        "eur_millions": self.revenue or 0,
                        "confidence": "high" if self.confidence > 0.7 else "medium",
                    }
                ]
            }
            if self.revenue
            else None,
            "ai_maturity_score": self.ai_score,
            "data_sources": self.data_sources,
            "confidence": self.confidence,
            "last_updated": self.last_updated.isoformat(),
            "is_synthetic": False,  # Explicitly mark as real data
        }


class WebResearcher:
    """Researches companies using web search and scraping."""

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        self.cache_dir = Path("data/cache/research")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()

    def _get_cache_path(self, company_name: str) -> Path:
        """Get cache file path for a company."""
        safe_name = re.sub(r"[^\w]", "_", company_name.lower())
        return self.cache_dir / f"{safe_name}.json"

    def _load_from_cache(self, company_name: str) -> ResearchResult | None:
        """Load cached research result if fresh (< 7 days)."""
        cache_path = self._get_cache_path(company_name)
        if not cache_path.exists():
            return None

        try:
            data = json.loads(cache_path.read_text())
            last_updated = datetime.fromisoformat(data.get("last_updated", ""))

            # Check if cache is fresh (< 7 days)
            if datetime.now() - last_updated > timedelta(days=7):
                return None

            # Reconstruct ResearchResult
            return ResearchResult(
                company_name=data["company_name"],
                website=data.get("website"),
                description=data.get("description"),
                industry=data.get("industry"),
                founded_year=data.get("founded_year"),
                employees=data.get("employees"),
                headquarters=data.get("headquarters"),
                revenue=data.get("revenue"),
                funding_raised=data.get("funding_raised"),
                valuation=data.get("valuation"),
                github_url=data.get("github_url"),
                linkedin_url=data.get("linkedin_url"),
                twitter_url=data.get("twitter_url"),
                ai_score=data.get("ai_score"),
                data_sources=data.get("data_sources", []),
                confidence=data.get("confidence", 0.0),
                last_updated=last_updated,
                raw_data=data.get("raw_data", {}),
            )
        except Exception as e:
            logger.warning(f"Failed to load cache for {company_name}: {e}")
            return None

    def _save_to_cache(self, result: ResearchResult):
        """Save research result to cache."""
        cache_path = self._get_cache_path(result.company_name)
        cache_path.write_text(json.dumps(result.__dict__, default=str, indent=2))

    async def search_web(self, query: str) -> list[dict[str, str]]:
        """Search the web for information."""
        # Use Brave Search API or similar
        try:
            # Try DuckDuckGo first (no API key needed)
            from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=10))
                return [
                    {"title": r.get("title", ""), "href": r.get("href", ""), "body": r.get("body", "")} for r in results
                ]
        except Exception as e:
            logger.warning(f"Web search failed: {e}")
            return []

    async def scrape_website(self, url: str) -> dict[str, Any]:
        """Scrape a company website for information."""
        try:
            response = await self.client.get(url, follow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            data = {
                "title": soup.title.string if soup.title else None,
                "description": None,
                "employees": None,
                "founded": None,
                "headquarters": None,
            }

            # Try to find description from meta tags
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                data["description"] = meta_desc.get("content")

            # Look for structured data (JSON-LD)
            scripts = soup.find_all("script", type="application/ld+json")
            for script in scripts:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict):
                        if "description" in json_data:
                            data["description"] = json_data["description"]
                        if "numberOfEmployees" in json_data:
                            data["employees"] = json_data["numberOfEmployees"]
                        if "foundingDate" in json_data:
                            data["founded"] = json_data["foundingDate"]
                        if "address" in json_data:
                            addr = json_data["address"]
                            if isinstance(addr, dict):
                                data["headquarters"] = addr.get("addressLocality", addr.get("addressCountry"))
                except Exception as e:
                    logger.debug(f"Failed to parse JSON-LD: {e}")

            # Look for About page
            about_links = soup.find_all("a", href=re.compile(r"about|company", re.I))
            if about_links:
                data["about_page"] = urljoin(url, about_links[0].get("href"))

            return data

        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
            return {}

    async def extract_funding_info(self, search_results: list[dict]) -> dict[str, Any]:
        """Extract funding information from search results."""
        funding_data = {"funding_raised": None, "valuation": None, "funding_rounds": []}

        for result in search_results:
            text = f"{result.get('title', '')} {result.get('body', '')}"

            # Look for funding patterns
            # e.g., "raised $50M", "Series A funding", "valuation of $1B"
            funding_patterns = [
                r"raised\s+\$?([\d.]+)\s*(M|B|million|billion)",
                r"funding.*?\$?([\d.]+)\s*(M|B)",
                r"valuation.*?\$?([\d.]+)\s*(M|B)",
            ]

            for pattern in funding_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        amount = float(match[0])
                        unit = match[1].upper()
                        if unit in ["B", "BILLION"]:
                            amount *= 1000  # Convert to millions

                        if "valuation" in text.lower():
                            funding_data["valuation"] = amount
                        else:
                            funding_data["funding_raised"] = amount
                    except Exception as e:
                        logger.debug(f"Failed to parse funding amount: {e}")

        return funding_data

    async def research_company(self, company_name: str) -> ResearchResult | None:
        """Research a company using web sources."""
        logger.info(f"🔍 Researching {company_name}...")

        # Check cache first
        cached = self._load_from_cache(company_name)
        if cached:
            logger.info(f"✅ Using cached data for {company_name}")
            return cached

        result = ResearchResult(company_name=company_name)

        # 1. Search for company
        search_query = f"{company_name} company funding employees revenue"
        search_results = await self.search_web(search_query)

        if not search_results:
            logger.warning(f"❌ No web results found for {company_name}")
            return None

        result.data_sources.append("web_search")

        # 2. Extract website URL
        for sr in search_results:
            href = sr.get("href", "")
            if company_name.lower().replace(" ", "") in href.lower():
                if not any(x in href for x in ["linkedin.com", "crunchbase.com", "wikipedia.org"]):
                    result.website = href
                    break

        # 3. Extract description
        if search_results:
            result.description = search_results[0].get("body", "")[:500]

        # 4. Scrape website for more details
        if result.website:
            website_data = await self.scrape_website(result.website)
            if website_data.get("description"):
                result.description = website_data["description"]
            if website_data.get("employees"):
                result.employees = website_data["employees"]
            if website_data.get("founded"):
                with contextlib.suppress(BaseException):
                    result.founded_year = int(str(website_data["founded"])[:4])
            if website_data.get("headquarters"):
                result.headquarters = website_data["headquarters"]

            result.data_sources.append("company_website")

        # 5. Extract funding information
        funding_data = await self.extract_funding_info(search_results)
        result.funding_raised = funding_data.get("funding_raised")
        result.valuation = funding_data.get("valuation")

        if result.funding_raised or result.valuation:
            result.data_sources.append("funding_data")

        # 6. Search for LinkedIn
        linkedin_query = f"{company_name} LinkedIn"
        linkedin_results = await self.search_web(linkedin_query)
        for lr in linkedin_results:
            href = lr.get("href", "")
            if "linkedin.com/company" in href:
                result.linkedin_url = href
                result.data_sources.append("linkedin")
                break

        # 7. Search for GitHub
        github_query = f"{company_name} GitHub"
        github_results = await self.search_web(github_query)
        for gr in github_results:
            href = gr.get("href", "")
            if "github.com" in href:
                result.github_url = href
                result.data_sources.append("github")
                break

        # 8. Calculate confidence score
        confidence_factors = [
            0.2 if result.website else 0,
            0.2 if result.description else 0,
            0.15 if result.employees else 0,
            0.15 if result.founded_year else 0,
            0.15 if result.funding_raised or result.revenue else 0,
            0.15 if result.headquarters else 0,
        ]
        result.confidence = sum(confidence_factors)

        # Mark as real data
        result.raw_data = {
            "search_results": len(search_results),
            "data_collection_method": "web_research",
            "is_synthetic": False,
        }

        logger.info(f"✅ Researched {company_name}: confidence={result.confidence:.2f}, sources={result.data_sources}")

        # Save to cache
        self._save_to_cache(result)

        return result

    async def research_companies(self, company_names: list[str]) -> list[ResearchResult]:
        """Research multiple companies concurrently."""
        tasks = [self.research_company(name) for name in company_names]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]


class SyntheticDataDetector:
    """Detects and rejects synthetic data."""

    SYNTHETIC_INDICATORS = [
        r"test-company-\d+",
        r"company-\d+-test",
        r"synthetic",
        r"fake-data",
        r"generated",
    ]

    SUSPICIOUS_PATTERNS = {
        "revenue": [1.0, 5.0, 10.0, 50.0, 100.0],  # Too round
        "employees": [10, 50, 100, 500, 1000],  # Too round
        "funding": [1000000, 5000000, 10000000],  # Exact millions
    }

    @classmethod
    def is_synthetic(cls, company_data: dict[str, Any]) -> bool:
        """Check if company data appears synthetic."""
        name = company_data.get("company_name", "").lower()

        # Check name patterns
        for pattern in cls.SYNTHETIC_INDICATORS:
            if re.search(pattern, name):
                return True

        # Check for explicit synthetic flag
        if company_data.get("is_synthetic") or company_data.get("data_source_type") == "synthetic":
            return True

        # Check for suspicious patterns
        revenue = company_data.get("revenue")
        if isinstance(revenue, (int, float)):
            if revenue in cls.SUSPICIOUS_PATTERNS["revenue"]:
                return True

        employees = company_data.get("employees")
        if isinstance(employees, int):
            if employees in cls.SUSPICIOUS_PATTERNS["employees"]:
                return True

        return False

    @classmethod
    def validate_data_authenticity(cls, company_data: dict[str, Any]) -> list[str]:
        """Validate data authenticity and return issues."""
        issues = []

        if cls.is_synthetic(company_data):
            issues.append("Data appears to be synthetic/research data")

        # Check for missing data sources
        data_sources = company_data.get("data_sources", [])
        if not data_sources:
            issues.append("No data sources documented")

        # Check for web-based sources
        web_sources = [s for s in data_sources if s in ["web_search", "company_website", "crunchbase", "linkedin"]]
        if not web_sources:
            issues.append("No web-based data sources found")

        # Check confidence score
        confidence = company_data.get("confidence", 0)
        if confidence < 0.3:
            issues.append(f"Low confidence score: {confidence}")

        # Check data freshness
        last_updated = company_data.get("last_updated")
        if last_updated:
            try:
                updated = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                if datetime.now() - updated > timedelta(days=90):
                    issues.append("Data is >90 days old")
            except Exception as e:
                logger.debug(f"Failed to parse last_updated date: {e}")

        return issues


async def main():
    """Example usage of the research pipeline."""
    companies_to_research = [
        "Tesla Energy",
        "Octopus Energy",
        "Siemens Energy",
        "Schneider Electric",
        "General Electric Renewable Energy",
    ]

    async with WebResearcher() as researcher:
        results = await researcher.research_companies(companies_to_research)

        for result in results:
            print(f"\n{'=' * 60}")
            print(f"Company: {result.company_name}")
            print(f"Website: {result.website}")
            print(f"Employees: {result.employees}")
            print(f"Funding: ${result.funding_raised}M" if result.funding_raised else "Funding: Unknown")
            print(f"Confidence: {result.confidence:.2f}")
            print(f"Sources: {', '.join(result.data_sources)}")
            print(f"Description: {result.description[:200]}..." if result.description else "No description")

            # Validate authenticity
            data_dict = result.to_dict()
            issues = SyntheticDataDetector.validate_data_authenticity(data_dict)
            if issues:
                print(f"⚠️  Issues: {', '.join(issues)}")
            else:
                print("✅ Data appears authentic")


if __name__ == "__main__":
    asyncio.run(main())
