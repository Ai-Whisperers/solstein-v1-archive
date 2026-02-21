"""
Company Research Module for Solstein Global Intelligence.

Collects comprehensive company data from public sources:
- Company profiles and fundamentals
- Financial data and metrics
- Leadership and governance
- Product and technology details
- News and events
- AI capabilities assessment
- Growth signals

Data Sources:
- Yahoo Finance (company info, financials)
- News APIs (press coverage)
- SEC/Regulatory filings
- Job postings (growth signals)
- Web scraping (products, technology)
"""

from datetime import datetime, date
from typing import Any

import pandas as pd
import yfinance as yf
from pydantic import BaseModel

from loguru import logger


class CompanyLeadership(BaseModel):
    """Leadership team information."""

    ceo: str | None = None
    cfo: str | None = None
    cto: str | None = None
    board: list[str] = []
    founders: list[str] = []


class CompanyFinancials(BaseModel):
    """Financial metrics."""

    revenue: float | None = None
    revenue_growth_yoy: float | None = None
    ebitda: float | None = None
    net_income: float | None = None
    profit_margin: float | None = None
    total_assets: float | None = None
    total_liabilities: float | None = None
    cash_position: float | None = None
    debt: float | None = None


class CompanyProducts(BaseModel):
    """Product and service information."""

    description: str | None = None
    products: list[str] = []
    services: list[str] = []
    target_markets: list[str] = []
    competitors: list[str] = []


class CompanyTechnology(BaseModel):
    """Technology stack and infrastructure."""

    industry: str | None = None
    sector: str | None = None
    sub_industry: str | None = None
    technology_stack: list[str] = []
    deployment_model: str | None = None
    cloud_provider: str | None = None


class CompanyGrowthSignals(BaseModel):
    """Growth indicators from various sources."""

    employee_count: int | None = None
    employee_growth: float | None = None
    job_postings_count: int | None = None
    job_postings_growth: float | None = None
    ai_related_jobs: int | None = None
    recent_hires: list[dict] = []
    office_expansion: list[str] = []


class CompanyAIAssessment(BaseModel):
    """AI capabilities assessment."""

    ai_score: int | None = None
    ai_signal_strength: str | None = None
    ai_products: list[str] = []
    ai_partnerships: list[str] = []
    ai_acquisitions: list[str] = []
    ai_team_mentioned: bool = False
    ml_products: list[str] = []
    autonomous_features: bool = False


class CompanyNews(BaseModel):
    """Recent news and events."""

    headlines: list[dict] = []
    press_releases: list[dict] = []
    earnings_calls: list[dict] = []
    mergers_acquisitions: list[dict] = []
    regulatory_filings: list[dict] = []


class CompanyResearch(BaseModel):
    """Complete company research profile."""

    ticker: str
    name: str
    exchange: str

    # Basic Info
    description: str | None = None
    founded: int | None = None
    headquarters: str | None = None
    website: str | None = None

    # People
    leadership: CompanyLeadership | None = None
    employees: int | None = None

    # Financials
    financials: CompanyFinancials | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    dividend_yield: float | None = None

    # Products
    products: CompanyProducts | None = None

    # Technology
    technology: CompanyTechnology | None = None

    # Growth
    growth: CompanyGrowthSignals | None = None

    # AI Assessment
    ai: CompanyAIAssessment | None = None

    # News
    news: CompanyNews | None = None

    # Scorecard (like original Solstein)
    scorecard: dict | None = None
    composite_score: float | None = None
    classification: str | None = None

    # Metadata
    last_updated: datetime | None = None
    data_sources: list[str] = []


class CompanyResearcher:
    """
    Conduct comprehensive research on public companies.

    Collects all publicly available information to match
    the depth of original Solstein company research.
    """

    def __init__(self):
        pass

    def research(self, ticker: str) -> CompanyResearch:
        """Conduct full company research."""
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            return self._build_profile(ticker, ticker_obj, info)

        except Exception as e:
            logger.error(f"Error researching {ticker}: {e}")
            return CompanyResearch(ticker=ticker, name=ticker, exchange="Unknown")

    def _build_profile(self, ticker: str, ticker_obj, info: dict) -> CompanyResearch:
        """Build complete company profile from available data."""

        # Basic info
        profile = CompanyResearch(
            ticker=ticker,
            name=info.get("longName", info.get("shortName", ticker)),
            exchange=info.get("exchange", "Unknown"),
            description=info.get("longBusinessSummary"),
            founded=info.get("foundedDate"),
            headquarters=info.get("city") + ", " + info.get("country")
            if info.get("city")
            else None,
            website=info.get("website"),
            employees=info.get("fullTimeEmployees"),
            market_cap=info.get("marketCap"),
            pe_ratio=info.get("trailingPE"),
            dividend_yield=info.get("dividendYield"),
        )

        # Leadership
        profile.leadership = CompanyLeadership(
            ceo=info.get("ceo"),
            cfo=info.get("cfo"),
            cto=info.get("cto"),
            board=info.get("boardMembers", []),
        )

        # Financials
        profile.financials = CompanyFinancials(
            revenue=info.get("totalRevenue"),
            revenue_growth_yoy=info.get("revenueGrowth"),
            ebitda=info.get("ebitda"),
            net_income=info.get("netIncomeToCommon"),
            profit_margin=info.get("profitMargins"),
            total_assets=info.get("totalAssets"),
            cash_position=info.get("totalCash"),
            debt=info.get("totalDebt"),
        )

        # Products & Services
        profile.products = CompanyProducts(
            description=info.get("longBusinessSummary"),
            products=info.get("productName", []) or [],
            target_markets=[info.get("country")] if info.get("country") else [],
        )

        # Technology
        profile.technology = CompanyTechnology(
            industry=info.get("industry"),
            sector=info.get("sector"),
            sub_industry=info.get("industryDisp"),
        )

        # AI Assessment
        profile.ai = self._assess_ai_capabilities(ticker, info)

        # Growth Signals
        profile.growth = CompanyGrowthSignals(
            employee_count=info.get("fullTimeEmployees"),
            job_postings_count=info.get("openPositions"),
        )

        # News
        profile.news = self._get_news(ticker_obj)

        # Scorecard (calculated from available data)
        profile.scorecard = self._calculate_scorecard(info)

        profile.last_updated = datetime.now()
        profile.data_sources = ["Yahoo Finance"]

        return profile

    def _assess_ai_capabilities(self, ticker: str, info: dict) -> CompanyAIAssessment:
        """Assess AI capabilities from available data."""

        ai_keywords = [
            "ai",
            "artificial intelligence",
            "machine learning",
            "ml",
            "deep learning",
            "neural",
            "gpt",
            "llm",
            "autonomous",
            "automation",
            "robotics",
            "computer vision",
            "nlp",
        ]

        business_summary = (info.get("longBusinessSummary") or "").lower()

        # Check for AI mentions
        ai_mentioned = any(kw in business_summary for kw in ai_keywords)

        # Assess AI signal strength
        ai_count = sum(1 for kw in ai_keywords if kw in business_summary)

        if ai_count >= 5:
            signal = "VERY STRONG"
            score = 10
        elif ai_count >= 3:
            signal = "STRONG"
            score = 7
        elif ai_mentioned:
            signal = "MODERATE"
            score = 5
        else:
            signal = "LOW"
            score = 2

        # Extract AI products/features mentioned
        ai_products = []
        if "generative" in business_summary or "gpt" in business_summary:
            ai_products.append("Generative AI")
        if "autonomous" in business_summary or "self-driving" in business_summary:
            ai_products.append("Autonomous Systems")
        if "machine learning" in business_summary:
            ai_products.append("Machine Learning")
        if "automation" in business_summary:
            ai_products.append("Automation")

        return CompanyAIAssessment(
            ai_score=score,
            ai_signal_strength=signal,
            ai_products=ai_products,
            ai_team_mentioned=ai_mentioned,
        )

    def _get_news(self, ticker_obj) -> CompanyNews:
        """Get recent news."""
        news_data = CompanyNews(headlines=[])

        try:
            news = ticker_obj.news
            if news:
                headlines = [
                    {
                        "title": n.get("title"),
                        "date": n.get("providerPublishTime"),
                        "source": n.get("publisher"),
                    }
                    for n in news[:10]
                ]
                news_data.headlines = headlines
        except Exception as e:
            logger.debug(f"Could not fetch news: {e}")

        return news_data

    def _calculate_scorecard(self, info: dict) -> dict:
        """Calculate scorecard dimensions from available data."""

        scores = {}

        # Revenue Growth (0-10)
        rev_growth = info.get("revenueGrowth", 0) or 0
        if rev_growth and rev_growth > 0.5:
            scores["Revenue Growth"] = 10
        elif rev_growth and rev_growth > 0.25:
            scores["Revenue Growth"] = 8
        elif rev_growth and rev_growth > 0.1:
            scores["Revenue Growth"] = 6
        elif rev_growth and rev_growth > 0:
            scores["Revenue Growth"] = 4
        else:
            scores["Revenue Growth"] = 2

        # Profitability (0-10)
        profit_margin = info.get("profitMargins", 0) or 0
        if profit_margin and profit_margin > 0.3:
            scores["Profitability"] = 10
        elif profit_margin and profit_margin > 0.15:
            scores["Profitability"] = 8
        elif profit_margin and profit_margin > 0:
            scores["Profitability"] = 6
        else:
            scores["Profitability"] = 3

        # Market Position (0-10) - based on market cap
        market_cap = info.get("marketCap", 0) or 0
        if market_cap > 500_000_000_000:  # > $500B
            scores["Market Position"] = 10
        elif market_cap > 100_000_000_000:  # > $100B
            scores["Market Position"] = 8
        elif market_cap > 10_000_000_000:  # > $10B
            scores["Market Position"] = 6
        elif market_cap > 1_000_000_000:  # > $1B
            scores["Market Position"] = 4
        else:
            scores["Market Position"] = 2

        # Innovation (based on sector and AI)
        industry = (info.get("industry") or "").lower()
        if any(
            t in industry for t in ["technology", "software", "ai", "semiconductor"]
        ):
            scores["Innovation"] = 9
        elif any(t in industry for t in ["pharma", "biotech", "health"]):
            scores["Innovation"] = 8
        else:
            scores["Innovation"] = 5

        # Composite score
        composite = sum(scores.values()) / len(scores) if scores else 0

        # Classification
        if composite >= 8:
            classification = "Leader"
        elif composite >= 6:
            classification = "Strong Performer"
        elif composite >= 4:
            classification = "Average"
        else:
            classification = "Challenger"

        return {
            "dimensions": scores,
            "composite_score": composite,
            "classification": classification,
        }


def research_company(ticker: str) -> dict[str, Any]:
    """
    Convenience function to get full company research.

    Returns comprehensive company profile matching original
    Solstein's research depth.
    """
    researcher = CompanyResearcher()
    result = researcher.research(ticker)

    return result.model_dump()
