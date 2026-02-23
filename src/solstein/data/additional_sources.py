"""
Additional Data Sources for Solstein Company Research.

This module provides infrastructure for:
- News API (press coverage, sentiment)
- Web scraping (product details, tech stack)
- LinkedIn data (hiring trends)
- Crunchbase/Funding data
- Patent data

To use these, you need API keys:

1. NEWS_API_KEY: Get from https://newsapi.org
2. CRUNCHBASE_KEY: Get from https://crunchbase.api-docs.io
3. PATENTSVIEW_API_KEY: Get from https://patentsview.org (free, 45 req/min)

For LinkedIn, we use web scraping (no official API available).
"""

import json
from datetime import date, datetime, timedelta
from typing import Any

import requests
from loguru import logger
from pydantic import BaseModel


class NewsArticle(BaseModel):
    """News article."""

    title: str
    description: str | None
    source: str
    url: str
    published_at: datetime
    sentiment: str | None = None


class PressCoverage(BaseModel):
    """Press coverage summary."""

    articles: list[NewsArticle]
    total_articles: int
    positive_count: int
    negative_count: int
    neutral_count: int
    sentiment_score: float | None


class LinkedInData(BaseModel):
    """LinkedIn hiring data."""

    company_name: str
    employee_count: int | None
    employee_growth_pct: float | None
    open_positions: int | None
    ai_related_positions: int | None
    recent_hires: list[dict] = []
    company_size: str | None = None


class FundingData(BaseModel):
    """Funding/investment data."""

    company_name: str
    total_raised: float | None
    last_round_amount: float | None
    last_round_date: date | None
    last_round_stage: str | None
    last_round_valuation: float | None
    investors: list[str] = []
    num_rounds: int = 0


class PatentData(BaseModel):
    """Patent data."""

    company_name: str
    total_patents: int
    recent_patents: list[dict] = []
    ai_related_patents: int
    top_patent_categories: list[str] = []


class ProductInfo(BaseModel):
    """Product information from web scraping."""

    company_name: str
    main_products: list[str]
    features: list[str]
    pricing_model: str | None
    target_customers: list[str] = []
    tech_stack: list[str] = []


class AdditionalDataSources:
    """
    Additional data sources for enhanced company research.

    Initialize with API keys to enable each source.
    """

    def __init__(
        self,
        news_api_key: str | None = None,
        crunchbase_key: str | None = None,
        patentsview_api_key: str | None = None,
    ):
        self.news_api_key = news_api_key
        self.crunchbase_key = crunchbase_key
        self.patentsview_api_key = patentsview_api_key
        self._patentsview_base_url = "https://search.patentsview.org/api/v1"

    # ====================
    # NEWS API
    # ====================

    def get_news(self, company_name: str, days_back: int = 30) -> PressCoverage:
        """
        Get news coverage for a company.

        First tries NewsAPI.org, falls back to web search if API unavailable.
        """
        if self.news_api_key:
            result = self._get_news_from_api(company_name, days_back)
            if result.total_articles > 0:
                return result
            logger.info("NewsAPI returned no results, trying web search fallback")

        return self._get_news_from_web_search(company_name, days_back)

    def _get_news_from_api(self, company_name: str, days_back: int) -> PressCoverage:
        """Get news using NewsAPI.org."""
        if not self.news_api_key:
            return PressCoverage(
                articles=[],
                total_articles=0,
                positive_count=0,
                negative_count=0,
                neutral_count=0,
                sentiment_score=None,
            )

        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": company_name,
            "from": from_date,
            "sortBy": "relevancy",
            "pageSize": 50,
            "apiKey": self.news_api_key,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            articles = []
            positive = 0
            negative = 0
            neutral = 0

            for article in data.get("articles", [])[:20]:
                published = article.get("publishedAt")
                if published:
                    published = datetime.fromisoformat(published.replace("Z", "+00:00"))

                sentiment = self._analyze_sentiment(article.get("title", "") + " " + (article.get("description") or ""))

                if sentiment == "positive":
                    positive += 1
                elif sentiment == "negative":
                    negative += 1
                else:
                    neutral += 1

                articles.append(
                    NewsArticle(
                        title=article.get("title", ""),
                        description=article.get("description"),
                        source=article.get("source", {}).get("name", "Unknown"),
                        url=article.get("url", ""),
                        published_at=published or datetime.now(),
                        sentiment=sentiment,
                    )
                )

            total = len(articles)
            sentiment_score = (positive - negative) / total if total > 0 else None

            return PressCoverage(
                articles=articles,
                total_articles=total,
                positive_count=positive,
                negative_count=negative,
                neutral_count=neutral,
                sentiment_score=sentiment_score,
            )

        except Exception as e:
            logger.error(f"Error fetching news from API: {e}")
            return PressCoverage(
                articles=[],
                total_articles=0,
                positive_count=0,
                negative_count=0,
                neutral_count=0,
                sentiment_score=None,
            )

    def _get_news_from_web_search(self, company_name: str, days_back: int) -> PressCoverage:
        """
        Get news using web search as fallback.

        This method is used when:
        - NewsAPI key is not configured
        - NewsAPI returns no results
        - NewsAPI quota is exhausted

        Uses Google search to find recent news articles.
        """
        from urllib.parse import quote

        try:
            search_url = f"https://www.google.com/search?q={quote(company_name)}+news&tbs=qdr:w"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            response = requests.get(search_url, headers=headers, timeout=15)
            html = response.text

            articles = []
            positive = 0
            negative = 0
            neutral = 0

            import re

            news_pattern = re.compile(r'<a href="(https?://[^"]+)"[^>]*>([^<]+)</a>')
            matches = news_pattern.findall(html)
            seen_urls = set()

            for url, title in matches[:20]:
                if any(
                    skip in url
                    for skip in [
                        "google",
                        "youtube",
                        "facebook",
                        "twitter",
                        "wikipedia",
                    ]
                ):
                    continue
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                sentiment = self._analyze_sentiment(title)
                if sentiment == "positive":
                    positive += 1
                elif sentiment == "negative":
                    negative += 1
                else:
                    neutral += 1

                articles.append(
                    NewsArticle(
                        title=title[:200] if title else "No title",
                        description=None,
                        source=url.split("/")[2] if len(url.split("/")) > 2 else "Web",
                        url=url,
                        published_at=datetime.now(),
                        sentiment=sentiment,
                    )
                )

            total = len(articles)
            sentiment_score = (positive - negative) / total if total > 0 else None

            if total > 0:
                logger.info(f"Found {total} news articles via web search for {company_name}")

            return PressCoverage(
                articles=articles,
                total_articles=total,
                positive_count=positive,
                negative_count=negative,
                neutral_count=neutral,
                sentiment_score=sentiment_score,
            )

        except Exception as e:
            logger.error(f"Error fetching news from web search: {e}")
            return PressCoverage(
                articles=[],
                total_articles=0,
                positive_count=0,
                negative_count=0,
                neutral_count=0,
                sentiment_score=None,
            )

    def _analyze_sentiment(self, text: str) -> str:
        """Simple keyword-based sentiment analysis."""
        text_lower = text.lower()

        positive_words = [
            "growth",
            "profit",
            "revenue",
            "success",
            "win",
            "launch",
            "expand",
            "innovation",
            "leader",
            "partnership",
            "award",
            "acquisition",
            "positive",
            "strong",
            "beat",
            "bullish",
        ]
        negative_words = [
            "loss",
            "lawsuit",
            "investigation",
            "scandal",
            "fire",
            "layoff",
            "bankruptcy",
            "decline",
            "weak",
            "miss",
            "warning",
            "fraud",
            "investor",
            "concern",
            "risk",
        ]

        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)

        if pos_count > neg_count + 1:
            return "positive"
        elif neg_count > pos_count + 1:
            return "negative"
        return "neutral"

    # ====================
    # WEB SCRAPING
    # ====================

    def scrape_company_website(self, company_name: str, website: str) -> ProductInfo:
        """
        Scrape company website for product information.

        Note: Be respectful of robots.txt and rate limits.
        """
        try:
            response = requests.get(
                website,
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0 (compatible; SolsteinBot/1.0)"},
            )
            response.raise_for_status()

            html = response.text.lower()

            # Extract potential product/feature keywords
            product_keywords = [
                "software",
                "platform",
                "solution",
                "service",
                "product",
                "app",
                "application",
                "tool",
                "system",
                "api",
                "cloud",
                "saas",
                "enterprise",
                "analytics",
                "ai",
                "ml",
                "machine learning",
                "automation",
                "digital",
                "mobile",
                "web",
                "dashboard",
            ]

            tech_keywords = [
                "python",
                "java",
                "javascript",
                "typescript",
                "react",
                "angular",
                "vue",
                "node",
                "aws",
                "azure",
                "gcp",
                "kubernetes",
                "docker",
                "sql",
                "postgresql",
                "mongodb",
                "redis",
                "graphql",
                "rest",
                "microservices",
                "microservice",
                "serverless",
                "lambda",
            ]

            products = [kw for kw in product_keywords if kw in html]
            tech_stack = [kw for kw in tech_keywords if kw in html]

            return ProductInfo(
                company_name=company_name,
                main_products=products[:10],
                features=[],
                pricing_model=None,
                target_customers=[],
                tech_stack=tech_stack[:10],
            )

        except Exception as e:
            logger.error(f"Error scraping {website}: {e}")
            return ProductInfo(
                company_name=company_name,
                main_products=[],
                features=[],
                tech_stack=[],
            )

    # ====================
    # CRUNCHBASE ALTERNATIVE (Using Public Data)
    # ====================

    def get_funding_data(self, company_name: str) -> FundingData:
        """
        Get funding data.

        Note: Crunchbase requires API key. This uses free sources.
        Alternative: Use PitchBook (paid), or manual research.
        """
        if not self.crunchbase_key:
            # Try using public sources
            return self._get_public_funding_data(company_name)

        # If API key provided, use Crunchbase API
        url = f"https://api.crunchbase.com/v4/organizations/{company_name}"
        headers = {"Authorization": f"Bearer {self.crunchbase_key}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return self._parse_crunchbase_data(data)
        except Exception as e:
            logger.error(f"Error fetching Crunchbase data: {e}")

        return FundingData(company_name=company_name)

    def _get_public_funding_data(self, company_name: str) -> FundingData:
        """Get funding data from public sources."""
        # This is limited - mainly just recent news about funding
        news = self.get_news(company_name, days_back=180)

        total_raised = None
        rounds = []

        for article in news.articles:
            title = article.title.lower()
            if "funding" in title or "raised" in title or "series" in title:
                rounds.append(
                    {
                        "title": article.title,
                        "date": article.published_at,
                        "source": article.source,
                    }
                )

        return FundingData(
            company_name=company_name,
            total_raised=total_raised,
            last_round_amount=None,
            last_round_date=None,
            last_round_stage=None,
            last_round_valuation=None,
            investors=[],
            num_rounds=len(rounds),
        )

    def _parse_crunchbase_data(self, data: dict) -> FundingData:
        """Parse Crunchbase API response."""
        props = data.get("properties", {})

        return FundingData(
            company_name=props.get("name", ""),
            total_raised=props.get("total_funding"),
            last_round_amount=props.get("last_funding_amount"),
            last_round_date=props.get("last_funded_at"),
            last_round_stage=props.get("last_funding_stage"),
            last_round_valuation=props.get("valuation"),
            investors=[],
            num_rounds=props.get("funding_rounds", 0),
        )

    # ====================
    # PATENT DATA (PatentsView API)
    # ====================

    def get_patent_data(self, company_name: str) -> PatentData:
        """
        Get patent data for a company using PatentsView API.

        Uses the PatentsView PatentSearch API to fetch patent information.
        API Docs: https://search.patentsview.org/docs/
        Rate limit: 45 requests/minute
        """
        if not self.patentsview_api_key:
            logger.warning("PatentsView API key not configured")
            return PatentData(
                company_name=company_name,
                total_patents=0,
                recent_patents=[],
                ai_related_patents=0,
                top_patent_categories=[],
            )

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
            "predictive model",
            "data science",
            "automation",
        ]

        try:
            headers = {"X-Api-Key": self.patentsview_api_key}

            query = {
                "_text_any": {"assignee_organization": company_name},
            }

            params = {
                "q": json.dumps(query),
                "f": json.dumps(
                    [
                        "patent_id",
                        "patent_title",
                        "patent_date",
                        "patent_abstract",
                        "assignee_organization",
                        "inventor_first_name",
                        "inventor_last_name",
                    ]
                ),
                "s": json.dumps([{"patent_date": "desc"}]),
                "o": json.dumps({"size": 50}),
            }

            response = requests.get(
                f"{self._patentsview_base_url}/patent",
                headers=headers,
                params=params,
                timeout=30,
            )

            if response.status_code == 403:
                logger.error("PatentsView API key invalid or forbidden")
                return PatentData(
                    company_name=company_name,
                    total_patents=0,
                    recent_patents=[],
                    ai_related_patents=0,
                    top_patent_categories=[],
                )

            if response.status_code != 200:
                logger.error(f"PatentsView API error: {response.status_code}")
                return PatentData(
                    company_name=company_name,
                    total_patents=0,
                    recent_patents=[],
                    ai_related_patents=0,
                    top_patent_categories=[],
                )

            data = response.json()

            total_patents = data.get("total_hits", 0)
            patents = data.get("patents", [])

            recent_patents = []
            ai_related_count = 0

            for patent in patents[:10]:
                patent_title = patent.get("patent_title", "").lower()
                patent_abstract = patent.get("patent_abstract", "").lower()

                combined_text = patent_title + " " + patent_abstract
                is_ai = any(ai_kw in combined_text for ai_kw in ai_keywords)
                if is_ai:
                    ai_related_count += 1

                recent_patents.append(
                    {
                        "patent_id": patent.get("patent_id"),
                        "title": patent.get("patent_title"),
                        "date": patent.get("patent_date"),
                        "abstract": patent.get("patent_abstract")[:200] + "..."
                        if patent.get("patent_abstract")
                        else None,
                    }
                )

            return PatentData(
                company_name=company_name,
                total_patents=total_patents,
                recent_patents=recent_patents,
                ai_related_patents=ai_related_count,
                top_patent_categories=[],
            )

        except requests.exceptions.Timeout:
            logger.error("PatentsView API request timed out")
            return PatentData(
                company_name=company_name,
                total_patents=0,
                recent_patents=[],
                ai_related_patents=0,
                top_patent_categories=[],
            )
        except Exception as e:
            logger.error(f"Error fetching patent data: {e}")
            return PatentData(
                company_name=company_name,
                total_patents=0,
                recent_patents=[],
                ai_related_patents=0,
                top_patent_categories=[],
            )

    # ====================
    # LINKEDIN (Scraping Alternative)
    # ====================

    def get_linkedin_data(self, company_name: str) -> LinkedInData:
        """
        Get LinkedIn hiring data.

        Note: LinkedIn has strict anti-scraping. Options:
        1. Use official LinkedIn API (requires partnership)
        2. Use third-party services (may violate ToS)
        3. Estimate from job postings elsewhere

        This returns placeholder - real implementation requires
        API integration or manual research.
        """
        # Try to find from news
        news = self.get_news(company_name, days_back=90)

        ai_related = 0
        for article in news.articles:
            title = article.title.lower()
            if any(w in title for w in ["hiring", "jobs", "recruit", "expansion"]):
                if any(w in title for w in ["ai", "engineer", "developer", "data"]):
                    ai_related += 1

        return LinkedInData(
            company_name=company_name,
            employee_count=None,
            employee_growth_pct=None,
            open_positions=None,
            ai_related_positions=ai_related,
            recent_hires=[],
            company_size=None,
        )


# ====================
# CONVENIENCE FUNCTION
# ====================


def get_all_company_data(
    ticker: str,
    news_api_key: str | None = None,
    crunchbase_key: str | None = None,
) -> dict[str, Any]:
    """
    Get comprehensive company data from all available sources.

    Returns:
        - Yahoo Finance data
        - News coverage
        - Funding data (if API key provided)
        - Patent data
    """
    from .company_research import research_company
    from .fetchers import GlobalMarketLoader

    results = {
        "ticker": ticker,
        "company_research": research_company(ticker),
        "market_data": None,
        "news": None,
        "funding": None,
        "patents": None,
    }

    # Get market data
    try:
        loader = GlobalMarketLoader()
        market = loader.get_stock_data(ticker)
        if market:
            results["market_data"] = {
                "price": market.current_price,
                "market_cap": market.market_cap,
                "eps_ttm": market.eps_ttm,
            }
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")

    # Get additional data sources
    additional = AdditionalDataSources(
        news_api_key=news_api_key,
        crunchbase_key=crunchbase_key,
    )

    # Get company name for other searches
    company_name = results["company_research"].get("name", ticker)

    # Get news
    results["news"] = additional.get_news(company_name)

    # Get funding (if API key)
    if crunchbase_key:
        results["funding"] = additional.get_funding_data(company_name)

    # Get patents
    results["patents"] = additional.get_patent_data(company_name)

    return results
